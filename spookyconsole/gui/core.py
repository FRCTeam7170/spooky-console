
"""
Core functionality for the GUI component of spooky-console.
"""

import tkinter as tk
import numpy as np
import asyncio
from collections import namedtuple
import spookyconsole.gui.style as style


Cell = namedtuple("Cell", ("column", "row"))
GridGeometry = namedtuple("GridGeometry", ("width", "height",
                                           "cell_width", "cell_height",
                                           "column_padding", "row_padding"))
HighlightVisual = namedtuple("HighlightVisual", ("bd_width", "bd_colour", "fill"))
GridVisual = namedtuple("GridVisual", ("width", "colour"))
DockableEntry = namedtuple("DockableEntry", ("id", "cell"))
Size = namedtuple("Size", ("width", "height"))
Point = namedtuple("Point", ("x", "y"))
BBox = namedtuple("BBox", ("x", "y", "w", "h"))


class ScrollCanvas(style.Canvas):
    """
    A tkinter canvas with horizontal and vertical scrollbars.

    Internally, a tkinter frame is used as the parent of the two scrollbars and the canvas, thus one mustn't attempt to
    use any of the geometry managers on the ``ScrollCanvas`` object itself, but rather its ``frame`` attribute::

        sc = ScrollCanvas(...)

        sc.frame.grid(...)
        # OR
        sc.frame.pack(...)
        # OR
        sc.frame.place(...)
        # BUT NOT
        sc.grid(...)
        # NOR
        sc.pack(...)
        # NOR
        sc.place(...)

    Note also that this class actually subclasses ``spookyconsole.gui.style.Canvas``, not the regular
    ``tkinter.Canvas``, meaning the styling conveniences provided in ``spookyconsole.gui.style`` may be utilized.

    This class handles binding both the scroll wheel movements (for vertical scrolling only) and mouse button 3 panning.
    If this object is constructed without the ``bind_all`` flag, additional (child) widgets may be bound through
    ``tag_widget`` so that they can accept mouse scroll/panning events and "relay" them to the canvas.
    """

    MAX_SCROLLBAR_POS = (0, 1)

    def __init__(self, master, width, height,
                 bind_all=False,
                 scroll_wheel_scale=1/2,
                 scroll_press_scale_x=1/2,
                 scroll_press_scale_y=1/2,
                 scroll_press_delay=50,
                 scrollbar_style=None,
                 frame_style=None,
                 *args, **kwargs):
        """
        :param master: The master tkinter widget for the frame containing the canvas and scrollbars.
        :param width: The width of the scroll region in pixels.
        :type width: int
        :param height: The height of the scroll region in pixels.
        :type height: int
        :param bind_all: Whether or not to bind mouse events globally or only on a tkinter bind class.
        :type bind_all: bool
        :param scroll_wheel_scale: A multiplier for vertical scrolling using the mouse wheel.
        :type scroll_wheel_scale: float
        :param scroll_press_scale_x: A multiplier for the horizontal scrolling using the third mouse button.
        :type scroll_press_scale_x: float
        :param scroll_press_scale_y: A multiplier for the vertical scrolling using the third mouse button.
        :type scroll_press_scale_y: float
        :param scroll_press_delay: How often (in milliseconds) to update the view when scrolling using the third mouse
        button.
        :type scroll_press_delay: int
        :param scrollbar_style: The style to apply to the x and y scrollbars. Defaults to the style given for the canvas
        (in kwargs).
        :type scrollbar_style: Style
        :param frame_style: The style to apply to the frame. Defaults to the style given for the canvas (in kwargs).
        :type frame_style: Style
        :param args: Additional args for the canvas constructor.
        :param kwargs: Additional kwargs for the canvas constructor.
        """
        # The default style to be used for the scrollbars and frame if they weren't given explicit styles.
        def_style = kwargs.get("style")
        scrollbar_style = scrollbar_style or def_style
        self.frame = style.Frame(master, style=(frame_style or def_style))
        super().__init__(self.frame, *args, **kwargs)

        self.x_scrollbar = style.Scrollbar(self.frame, style=scrollbar_style, command=self.xview, orient=tk.HORIZONTAL)
        self.y_scrollbar = style.Scrollbar(self.frame, style=scrollbar_style, command=self.yview)
        self.configure(xscrollcommand=self.x_scrollbar.set, yscrollcommand=self.y_scrollbar.set,
                       xscrollincrement=1, yscrollincrement=1, scrollregion=(0, 0, width, height))

        self.grid(row=0, column=0, sticky=tk.NSEW)
        self.x_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        self.y_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # Here we essentially make only the canvas (not the scrollbars) grow in accordance with any new space.
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.scroll_wheel_scale = scroll_wheel_scale
        self.scroll_press_scale_x = scroll_press_scale_x
        self.scroll_press_scale_y = scroll_press_scale_y
        self.scroll_press_delay = scroll_press_delay

        # Some state variables involved with the process of panning with mouse button 3.
        self._wheel_drag_start_pos = None
        self._wheel_drag_delta_x = 0
        self._wheel_drag_delta_y = 0

        # Bindings. Note that what tkinter considers mouse button 2 (the scroll click) is more typically called mouse
        # button 3 (which is what I have been referring to it as).
        if bind_all:
            self.bind_all("<MouseWheel>", self._wheel_scroll)
            self.bind_all("<Button-2>", self._wheel_press)
            self.bind_all("<B2-Motion>", self._wheel_motion)
            self.bind_all("<ButtonRelease-2>", self._wheel_release)
        else:
            self.tag_widget(self)
            self.bind_class(self.bind_class_name, "<MouseWheel>", self._wheel_scroll)
            self.bind_class(self.bind_class_name, "<Button-2>", self._wheel_press)
            self.bind_class(self.bind_class_name, "<B2-Motion>", self._wheel_motion)
            self.bind_class(self.bind_class_name, "<ButtonRelease-2>", self._wheel_release)

    @property
    def bind_class_name(self):
        """
        :return: A unique identifier to be used as a tkinter bind class.
        :rtype: str
        """
        return "ScrollCanvas{}".format(id(self))

    def tag_widget(self, widget):
        """
        Add this ``ScrollCanvas``'s unique bind class to a tkinter widget so that said widget "relays" its mouse events
        (namely, scrolling and panning with mouse button 3) to the canvas. This will have no effect if the canvas was
        constructed with the ``bind_all`` flag, in which case the given widget should already "relay" its mouse events
        to the canvas.

        :param widget: The tkinter widget to add the tag to.
        """
        # widget.bindtags() with no argument returns the current bind tags.
        widget.bindtags((self.bind_class_name,) + widget.bindtags())

    def resize_scroll_region(self, width, height):
        """
        Convenience method for resizing the canvas's scroll region.

        :param width: The new width in pixels.
        :type width: int
        :param height: The new height in pixels.
        :type height: int
        """
        self.configure(scrollregion=(0, 0, width, height))

    def _wheel_scroll(self, event):
        """
        Internal method used as the callback for "<MouseWheel>" events.

        :param event: The tkinter event object.
        """
        # if self.y_scrollbar.get() != self.MAX_SCROLLBAR_POS:
        self.yview_scroll(-1 * int(event.delta * self.scroll_wheel_scale), tk.UNITS)

    def _wheel_press(self, event):
        """
        Internal method used as the callback for "<Button-2>" (scroll click) events.

        :param event: The tkinter event object.
        """
        # Set the cursor. "fleur" is a 4-directional arrow typical to panning.
        self.configure(cursor="fleur")
        # Record the starting mouse position of the pan. This is used to calculate how far from the mouse has moved from
        # this starting position and ultimately has sensitive the panning should be.
        self._wheel_drag_start_pos = Point(event.x, event.y)
        # Start the update view callback, which is called repeatedly while the mouse click is held.
        self._wheel_press_update_view()

    def _wheel_motion(self, event):
        """
        Internal method used as the callback for "<B2-Motion>" (scroll click motion) events.

        :param event: The tkinter event object.
        """
        # if self.x_scrollbar.get() != self.MAX_SCROLLBAR_POS:
        # Record the x distance moved from the starting position.
        self._wheel_drag_delta_x = event.x - self._wheel_drag_start_pos.x
        # if self.y_scrollbar.get() != self.MAX_SCROLLBAR_POS:
        # Record the y distance moved from the starting position.
        self._wheel_drag_delta_y = event.y - self._wheel_drag_start_pos.y

    def _wheel_release(self, _):
        """Internal method used as the callback for "<ButtonRelease-2>" (scroll click release) events."""
        # Reconfigure the mouse cursor to the standard arrow.
        self.configure(cursor="left_ptr")
        # Reset all the state variables associated with panning. Note that setting the _wheel_drag_start_pos variable to
        # None effectively cancels the view update callback since it uses whether that variable is set as an indicator
        # for whether or not the user is panning.
        self._wheel_drag_start_pos = None
        self._wheel_drag_delta_x = 0
        self._wheel_drag_delta_y = 0

    def _wheel_press_update_view(self):
        """
        Internal method scheduled by itself with ``tkinter.Misc.after`` to repeatedly update the canvas's view. This
        chained calling is initiated in ``ScrollCanvas._wheel_press`` and stops once ``ScrollCanvas._wheel_release``
        unsets ``ScrollCanvas._wheel_drag_start_pos``.
        """
        # Notice the scroll speed is proportional to the how far the mouse has been moved from when the mouse scroll
        # click started and to the appropriate scale factor.
        self.xview_scroll(int(self._wheel_drag_delta_x * self.scroll_press_scale_x), tk.UNITS)
        self.yview_scroll(int(self._wheel_drag_delta_y * self.scroll_press_scale_y), tk.UNITS)
        if self._wheel_drag_start_pos:
            self.after(self.scroll_press_delay, self._wheel_press_update_view)


class GridState(np.ndarray):
    """
    A wrapper around a numpy array of booleans for storing the state of a ``Grid`` instance. That is, each element in
    the ``GridState`` stores whether or not the corresponding grid cell is populated (i.e. contains part of a
    ``DockableMixin`` widget).

    A numpy array in particular is used for this purpose chiefly for the convenience provided by fancy indexing. This
    makes checking for grid conflicts with a prospect dockable placement rather simple (and fast).
    """

    def __new__(cls, width, height):
        """
        (Numpy does initialization in ``__new__``, not ``__init__``!)

        :param width: The width of the grid to be represented by this array.
        :type width: int
        :param height: The height of the grid to be represented by this array.
        :type height: int
        :return: The new ``GridState`` object, initialized to all false values.
        :rtype: GridState
        """
        obj = super().__new__(cls, (height, width), dtype=bool)
        obj.fill(False)
        return obj

    @property
    def min_width(self):
        """
        :return: The minimum width the grid may be shrunk to before a dockable would be "clipped".
        :rtype: int
        """
        try:
            # Sum the columns and find the maximum (i.e. last) index in which a column sums to zero (indicating no cells
            # in that column are populated).
            return np.where(self.sum(axis=0) > 0)[0].max() + 1
        except ValueError:
            return 0

    @property
    def min_height(self):
        """
        :return: The minimum height the grid may be shrunk to before a dockable would be "clipped".
        :rtype: int
        """
        try:
            # Sum the rows and find the maximum (i.e. last) index in which a row sums to zero (indicating no cells in
            # that row are populated).
            return np.where(self.sum(axis=1) > 0)[0].max() + 1
        except ValueError:
            return 0

    def empty_copy(self):
        """
        :return: An empty copy (i.e. same size) of the grid.
        :rtype: GridState
        """
        return GridState(*self.shape)

    def conflicts(self, cell, col_span, row_span):
        """
        Determine whether a dockable with the given dimensions placed at the given cell would conflict with the current
        grid state (i.e. one or more dockables would "overlap").

        :param cell: The prospect top-left coordinate of the dockable.
        :type cell: Cell
        :param col_span: The column span of the dockable.
        :type col_span: int
        :param row_span: The row span of the dockable.
        :type row_span: int
        :return: Whether or not a conflict would occur.
        :rtype: bool
        """
        col, row = cell
        return self[row:row+row_span, col:col+col_span].any()

    def conflicts_where(self, cell, col_span, row_span):
        """
        Determine each location in which a dockable with the given dimensions placed at the given cell would conflict
        with the current grid state (i.e. one or more dockables would "overlap") and return the result as a copy of this
        grid state.

        :param cell: The prospect top-left coordinate of the dockable.
        :type cell: Cell
        :param col_span: The column span of the dockable.
        :type col_span: int
        :param row_span: The row span of the dockable.
        :type row_span: int
        :return: A ``GridState`` object in which every conflict is represented by a true value in the corresponding
        cell.
        :rtype: GridState
        """
        return self.empty_copy().populate(cell, col_span, row_span) & self

    def populate(self, cell, col_span, row_span):
        """
        "Populate" the grid state so as to a reflect a dockable with the given dimensions placed at the given cell. Note
        that this method does not check for any grid conflicts beforehand; grid conflicts checks must be performed by
        the caller.

        :param cell: The top-left coordinate of the dockable.
        :type cell: Cell
        :param col_span: The column span of the dockable.
        :type col_span: int
        :param row_span: The row span of the dockable.
        :type row_span: int
        """
        self._set(cell, col_span, row_span, True)

    def unpopulate(self, cell, col_span, row_span):
        """
        "Unpopulate" the grid state so as to a reflect a dockable with the given dimensions initially at the given cell
        being removed.

        :param cell: The top-left coordinate of the dockable.
        :type cell: Cell
        :param col_span: The column span of the dockable.
        :type col_span: int
        :param row_span: The row span of the dockable.
        :type row_span: int
        """
        self._set(cell, col_span, row_span, False)

    def _set(self, cell, col_span, row_span, val):
        """
        Internal function to set a group of cells in the grid to the given value.

        :param cell: The top-left coordinate of the cell group.
        :type cell: Cell
        :param col_span: The width of the dockable.
        :type col_span: int
        :param row_span: The height of the dockable.
        :type row_span: int
        """
        col, row = cell
        self[row:row+row_span, col:col+col_span] = val


class Grid(ScrollCanvas):
    """
    The Grid class is a scrollable canvas with a draggable snapping/docking mechanism so that child widgets are forced
    to a rigid grid layout all while permitting manual movement of the widgets at runtime. A canvas is used as the
    parent widget since this allows the creation of special effects (discussed below) when any child widget is dragged.
    Further, a canvas is a desirable parent widget because when inappropriately large child widgets are placed on a
    canvas via ``tkinter.Canvas.create_window``, they are simply clipped as opposed to enlarging each column or row
    which they occupy, which would contradict the grid's rigid layout philosophy.

    The widgets that can be registered on the grid must be subclasses of ``DockableMixin`` (a single instance of which
    is hereby to be interchangeably referred to simply as a "dockable"), a mixin class that provides the foundation for
    the dragging mechanism (namely, dockables bind to right click events which are then relayed to this class). Each
    dockable specifies a certain column and row span which determines how many grid "cells" it should consume in either
    direction. These column and row spans are used along with the grid coordinate of the dockable's top-left cell to
    describe its position and which cells on the grid it consumes. When dockables are first registered to the grid
    (via ``Grid.register_dockable``), their initial position on the grid will be the cell nearest to the top-left corner
    of the grid which can accommodate the dockable without resulting in a "grid conflict" (i.e. when two or more
    dockables overlap on the grid). Afterwards, the position of the dockable can be changed manually through the gui or
    programmatically through ``DockableMixin.move_dockable``. When dragging the dockable with the mouse, the nearest
    valid (i.e. will not result in a grid conflict) grid cell is taken as the dockable's top-left coordinate. The size
    of a dockable may also be programmatically changed via ``DockableMixin.resize_dockable``.

    The ``GridState`` class is responsible for storing the current state of the grid (i.e. which cells are "populated"
    by dockables and which are not). See ``GridState`` for information.

    The geometry of the grid is defined by six values: width, height, cell width, cell height, column padding, and row
    padding. All of these are stored in ``Grid.geometry``, an instance of the namedtuple ``GridGeometry``. They are all
    settable via ``Grid.set_geometry``. ``width`` and ``height`` refer to the dimensions of the grid in cells;
    ``cell_width`` and ``cell_height`` refer to the dimensions of each grid cell in pixels; ``column_padding`` and
    ``row_padding`` refer to the spacing between grid cells in pixels. The space allocated to any given dockable is
    determined by its column and row span and the grid's cell width and cell height; the grid's column or row padding
    will also effect the dockable's allocated space if the dockable's column or row span are greater than one,
    respectively. If a dockable is not allocated enough space, it will be clipped (as discussed above).

    Whenever a dockable is manually dragged in the gui it is removed (un-drawn) from the screen and in its place a
    "highlighting" rectangle, sized to the bounding box of the dockable, appears. This visual serves as the user's guide
    for where the dockable would be placed if they were to stop dragging the dockable. Three parameters control the
    appearance of this rectangle: border width and colour, and fill colour. They are stored in
    ``Grid.highlight_visual``, an instance of the namedtuple ``HighlightVisual``. They are all settable via
    ``Grid.set_highlight_visual``.

    Another visual effect that occurs whenever a dockable is manually dragged in the gui are grid cell outlines. These
    are rectangles that surround each cell of the grid, thereby serving as the user's guide for where each cell is
    delimited. Two parameters control the appearance of these rectangles: border width and colour. They are stored in
    ``Grid.grid_visual``, an instance of the namedtuple ``GridVisual``. They are all settable via
    ``Grid.set_grid_visual``.

    Whenever the window containing a grid is resized, two things may happen: (1) if the grid's scroll region is not
    fully expanded, the grid's "viewport" (how much of the scroll region is visible at once) shrinks or expands as
    appropriate; (2) if the grid's scroll region is fully expanded, the grid's "resize protocol" comes into effect. The
    grid's resize protocol is stored in ``Grid.resize_protocol`` and settable through ``Grid.set_resize_protocol``.
    The resize protocol determines how any new screen space allocated to the grid should be distributed among its child
    widgets. See ``Grid.resize_protocol`` for more information.
    """

    # Some minimums regarding geometry.
    MIN_CELL_WIDTH = 25
    MIN_CELL_HEIGHT = 25

    # Canvas tag constants.
    TAG_GRIDLINE = "gridline"
    TAG_HIGHLIGHT = "highlight"

    # Grid resize protocols.
    RESIZE_PROTO_NONE = 0
    RESIZE_PROTO_EXPAND_CELLS = 1
    RESIZE_PROTO_ADD_PADDING = 2

    # How frequently in milliseconds to update this grid's geometry when the window size is changed.
    RESIZE_UPDATE_DELAY = 50  # ms

    def __init__(self, master, width, height,
                 cell_width=50, cell_height=50,
                 column_padding=0, row_padding=0,
                 resize_protocol=RESIZE_PROTO_EXPAND_CELLS,
                 highlight_visual=HighlightVisual(2, style.GRAY_SCALE_2, style.GRAY_SCALE_4),
                 grid_visual=GridVisual(1, style.GRAY_SCALE_0),
                 *args, **kwargs):
        """
        :param master: The master widget for the canvas.
        :param width: Initial amount of columns in the grid.
        :type width: int
        :param height: Initial amount of rows in the grid.
        :type height: int
        :param cell_width: Initial width (in pixels) of each cell in the grid.
        :type cell_width: int
        :param cell_height: Initial height (in pixels) of each cell in the grid.
        :type cell_height: int
        :param column_padding: Initial padding between columns in the grid.
        :type column_padding: int
        :param row_padding: Initial padding between rows in the grid.
        :type row_padding: int
        :param resize_protocol: Initial protocol to employ when window size changes past scroll region.
        :param highlight_visual: Initial specification for how the highlight effect shall appear.
        :type highlight_visual: HighlightVisual
        :param grid_visual: Initial specification for how the grid effect shall appear.
        :type grid_visual: GridVisual
        :param args: Extra args for the canvas constructor.
        :param kwargs: Extra kwargs for the canvas constructor.
        """
        super().__init__(master,
                         width * (cell_width + column_padding),
                         height * (cell_height + row_padding),
                         *args, **kwargs)

        self._curr_dockable = None
        """Stores a reference to the ``DockableMixin`` currently being dragged, if one exists."""

        self._curr_dockable_orig_cell = None
        """Stores the currently-being-dragged ``DockableMixin``'s cell before the drag initiated."""

        self._curr_cell = None
        """The top-left ``Cell`` of the group of cells currently being hovered over."""

        self._grid_state = GridState(width, height)
        """Stores/manages which cells are populated."""

        self._dockables = {}
        """
        A dictionary whose keys are all the ``DockableMixin``s registered to this grid and whose values are
        ``DockableEntry``s.
        """

        self.geometry = GridGeometry(width, height, cell_width, cell_height, column_padding, row_padding)
        """The grid's current ``GridGeometry``."""

        self.orig_geometry = self.geometry
        """Stores the geometry (as a ``GridGeometry``) before any changes from window resizing are made."""

        self._resize_data = None
        """A ``Size`` tuple to cache the parent window's width and height while it's being resized."""

        self._resize_after_id = None
        """
        Stores the callback id for ``Grid._resize_after_callback`` so it may be cancelled when the
        ``Grid.resize_protocol`` changes.
        """

        self.highlight_visual = highlight_visual
        """The current ``HighlightVisual`` for the highlighting effect."""

        self.grid_visual = grid_visual
        """The current ``GridVisual`` for the grid drawn while a ``DockableMixin`` is dragged."""

        self.resize_protocol = None
        """
        An integer representing the protocol to employ when the parent window is resized such that the grid's canvas is
        granted more space than required by its current scrollregion.
        
        May be one of the following:
            - ``Grid.RESIZE_PROTO_NONE``: Do nothing when the window is resized.
            - ``Grid.RESIZE_PROTO_EXPAND_CELLS``: Expand each cell equally to fit any new space when the window is\
            resized.
            - ``Grid.RESIZE_PROTO_ADD_PADDING``: Add padding equally in between each column or row when the window\
            is resized.
        
        """

        self.set_resize_protocol(resize_protocol)

    def register_dockable(self, dockable):
        """
        Register a ``DockableMixin`` to be managed by this grid. Its tkinter parent must already be this grid.

        Registered dockables should never be manually (i.e. ``dockable.configure(...)``) positioned, have their width
        and height manually changed, etcetera. Instead use the appropriate methods on ``DockableMixin`` objects.

        :param dockable: The dockable to be managed by this grid.
        :type dockable: DockableMixin
        """
        # Find an initial position for this dockable.
        cell = self._find_next_empty_cell_group(dockable.col_span, dockable.row_span)
        self._place_dockable(dockable, cell)
        # Tag the dockable so that scrolling works on it.
        self.tag_widget(dockable)

    def move_dockable(self, dockable, cell):
        """
        Move the given ``DockableMixin`` ``dockable`` to the given ``Cell`` ``cell``. If there is a grid conflict, this
        will fail and no changes will be made.

        :param dockable: The dockable to move.
        :type dockable: DockableMixin
        :param cell: The cell to move the dockable to.
        :type cell: Cell
        :return: Whether or not the move was successful.
        :rtype: bool
        """
        old_cell = self._dockables[dockable].cell
        conflicts_array = self._grid_state.conflicts_where(cell, dockable.col_span, dockable.row_span)
        # conflicts_indices stores all the indices of grid conflicts, if any, in columns.
        conflicts_indices = np.vstack(np.where(conflicts_array))
        # Loop over all the conflicts (if there are any) and assure that they take place in the dockable's previous
        # position, since it's being removed anyway so these conflicts are irrelevant. If any of the conflicts are
        # "genuine", this conditional will not succeed and no changes are made.
        if all(self._contained_in(Cell(idx[1], idx[0]), old_cell, dockable.col_span, dockable.row_span)
               for idx in conflicts_indices.T):
            self.remove_dockable(dockable)
            self._place_dockable(dockable, cell)
            return True
        return False

    def dockable_resized(self, dockable):
        """
        Signal to this grid that the ``DockableMixin`` ``dockable``'s ``DockableMixin.col_span`` and/or
        ``DockableMixin.row_span`` has been changed, and thus it must be redrawn and its position must be recalculated.
        If it must be moved, it will be moved as little as possible. If no where on the grid satisfies its new size, the
        grid is expanded horizontally as needed to accommodate the ``dockable``.

        :param dockable: The dockable that has been resized.
        :type dockable: DockableMixin
        """
        old_cell = self._dockables[dockable].cell
        self.remove_dockable(dockable)
        cell = self._find_next_empty_cell_group(dockable.col_span, dockable.row_span, old_cell)
        self._place_dockable(dockable, cell)

    def _place_dockable(self, dockable, cell):
        """
        Internal method to place the ``DockableMixin`` ``dockable`` at the given ``Cell`` ``cell``, populate the
        ``Grid._grid_state`` appropriately, and add the ``dockable`` to the ``Grid._dockables`` dictionary. This method
        does not check for grid conflicts.

        :param dockable: The dockable to place.
        :type dockable: DockableMixin
        :param cell: The cell to place the dockable at.
        :type cell: Cell
        """
        self._grid_state.populate(cell, dockable.col_span, dockable.row_span)
        bbox = self._calc_bbox(cell, dockable.col_span, dockable.row_span)
        id_ = self.create_window(bbox.x, bbox.y, width=bbox.w, height=bbox.h, anchor=tk.NW, window=dockable)
        self._dockables[dockable] = DockableEntry(id_, cell)

    def remove_dockable(self, dockable):
        """
        Remove the given ``DockableMixin`` ``dockable`` from the grid. This method is functionally the opposite of
        ``Grid._place_dockable``.

        :param dockable: The dockable to remove.
        :type dockable: DockableMixin
        """
        id_, cell = self._dockables.pop(dockable)
        self.delete(id_)
        self._grid_state.unpopulate(cell, dockable.col_span, dockable.row_span)

    def _calc_bbox(self, cell, col_span, row_span):
        """
        Calculate the bounding box (bbox) in canvas pixels described by the given information.

        :param cell: The top-left cell of the box.
        :type cell: Cell
        :param col_span: The width of the box in cells.
        :type col_span: int
        :param row_span: The height of the box in cells.
        :type row_span: int
        :return: The calculated bbox.
        :rtype: BBox
        """
        x = cell.column * (self.geometry.cell_width + self.geometry.column_padding)
        y = cell.row * (self.geometry.cell_height + self.geometry.row_padding)
        w = col_span * self.geometry.cell_width + (col_span - 1) * self.geometry.column_padding
        h = row_span * self.geometry.cell_height + (row_span - 1) * self.geometry.row_padding
        return BBox(x, y, w, h)

    def _find_next_empty_cell_group(self, col_span, row_span, from_=Cell(0, 0)):
        """
        Find an unpopulated rectangular group of cells with dimensions ``col_span`` (width) by ``row_span`` (height) and
        return the top-left cell coordinate. This method uses the ``Grid._naive_search`` algorithm with ``from_`` as the
        origin cell, meaning it will attempt to find the cell group nearest to ``from_``.

        If such a cell does not exist, the grid is expanded so as to fit such a rectangular group of cells. More
        specifically, we first ensure the grid height is greater than or equal to ``row_span``, then we expand the grid
        horizontally as few columns as possible so that the specified rectangular group of cells may fit in the
        top-right corner of the grid.

        :param col_span: The width of the unpopulated cell group to find.
        :type col_span: int
        :param row_span: The height of the unpopulated cell group to find.
        :type row_span: int
        :param from_: The cell to start the search from.
        :type from_: Cell
        :return: The coordinate of the top-left cell in the cell group.
        :rtype: Cell
        """
        # First try to find a preexisting group of cells.
        cell = self._naive_search(from_, col_span, row_span)
        if cell is not None:
            return cell

        # In the event of failing to find a preexisting group of cells, expand the grid.
        # First, determine if the height must be increased.
        new_height = row_span if row_span > self.geometry.height else None
        # coln will refer to how many columns at the right side of the grid are empty for at least the first row_span
        # rows. This way, we need only expand the grid by col_span - coln. How the below line achieves this is left as a
        # challenge to the reader :)
        try:
            coln = np.where(self._grid_state[:row_span, ::-1].sum(axis=0) == 0)[0].min() + 1
        except ValueError:
            coln = 0
        # Expand the grid according to the newly found width and height.
        self.set_geometry(self.geometry.width + col_span - coln, new_height)
        return Cell(self.geometry.width - col_span, 0)

    def _naive_search(self, origin_cell, col_span, row_span):
        """
        Search the grid around ``origin_cell`` for a rectangular group of cells with dimensions ``col_span`` (width) by
        ``row_span`` (height) and return the top-left cell. The group of cells nearest to ``origin_cell`` is returned,
        where nearest is defined as the smallest sum of positive column offset and positive row offset from
        ``origin_cell``.

        :param origin_cell: The cell to search around.
        :type origin_cell: Cell
        :param col_span: The width of the rectangular group of cells to search for.
        :type col_span: int
        :param row_span: The height of the rectangular group of cells to search for.
        :type row_span: int
        :return: The top-left cell in the group or None if no such group of cells can be found.
        :type: Cell
        """
        col, row = origin_cell
        lco = -col  # Lower Column Offset limit
        uco = self.geometry.width - col - col_span  # Upper Column Offset limit
        lro = -row  # Lower Row Offset limit
        uro = self.geometry.height - row - row_span  # Upper Row Offset limit
        # Gradually increase the search radius, mag(nitude). mag = 0 corresponds to the origin_cell itself; mag = 1
        # corresponds to the 8 cells around the origin cell; mag = 2 corresponds to the 16 cells around those 8 cells;
        # etc.
        for mag in range(max(self.geometry.width - col, self.geometry.height - row, col + 1, row + 1)):
            # This generates all the valid offsets from the origin_cell as (c, r) two-tuples for a given mag.
            offsets = ((c, r) for c in range(-mag, mag + 1) for r in range(-mag, mag + 1)
                       if abs(c) + abs(r) >= mag if lco <= c <= uco if lro <= r <= uro)
            # Sort the offsets based on their absolute sum so that we can return the nearest group of cells.
            for c_offset, r_offset in sorted(offsets, key=lambda o: abs(o[0]) + abs(o[1])):
                candidate = Cell(col + c_offset, row + r_offset)
                # Only return the candidate cell if it has no grid conflicts
                if not self._grid_state.conflicts(candidate, col_span, row_span):
                    return candidate

    def signal_drag_start(self, dockable):
        """
        Called by the ``DockableMixin`` dockable widget to signal that it is being dragged.

        :param dockable: The dockable who's being dragged.
        :type dockable: DockableMixin
        """
        self._draw_grid()
        self._curr_dockable = dockable
        self._curr_dockable_orig_cell = self._dockables[dockable].cell
        self.remove_dockable(dockable)
        # Despite the user not actually moving the mouse, call signal_drag_motion so that the highlight appears on the
        # grid.
        self.signal_drag_motion()

    def signal_drag_stop(self):
        """Called by a ``DockableMixin`` widget to signal that it has stopped being dragged."""
        self._clear_grid()
        self._clear_highlight()
        if self._curr_cell:
            # If the user released the drag in a valid position, used this new position for the dockable's position.
            self._place_dockable(self._curr_dockable, self._curr_cell)
            self._curr_cell = None
        else:
            # If the user released the drag in a invalid position, revert to the dockable's old position.
            self._place_dockable(self._curr_dockable, self._curr_dockable_orig_cell)
        self._curr_dockable = None
        self._curr_dockable_orig_cell = None

    def signal_drag_motion(self):
        """Called by a ``DockableMixin`` widget currently being dragged to signal that the mouse has moved."""
        self._clear_highlight()
        self._curr_cell = None

        # Find the cell over which the cursor has moved to.
        # Note the calls to canvasx and canvasy; these are necessary since the canvas is scrollable and the mouse_x and
        # mouse_y coordinates are relative to the root window, not the canvas.
        mouse_x = self.winfo_pointerx() - self.winfo_rootx()
        mouse_y = self.winfo_pointery() - self.winfo_rooty()
        col, row = self._find_nearest_cell(self.canvasx(mouse_x), self.canvasy(mouse_y))
        # Alias the col and row span for conciseness.
        col_span = self._curr_dockable.col_span
        row_span = self._curr_dockable.row_span

        # If the column and row are too big or too small (i.e. the dockable wouldn't fit in the grid at this cell
        # regardless of grid conflicts), clamp them down to the maximums/minimums.
        max_col = self.geometry.width - col_span
        if col > max_col:
            col = max_col
        elif col < 0:
            col = 0
        max_row = self.geometry.height - row_span
        if row > max_row:
            row = max_row
        elif row < 0:
            row = 0
        # Note that this search should never return None since the dockable can at least return to its previous
        # position.
        cell = self._naive_search(Cell(col, row), col_span, row_span)

        self._set_highlight(cell, col_span, row_span)
        self._curr_cell = cell

    def _find_nearest_cell(self, x, y):
        """
        Internal method to find the ``Cell`` nearest to the given ``x`` and ``y`` coordinates relative to the canvas.

        :param x: The x coordinate relative to the canvas.
        :type x: int
        :param y: The y coordinate relative to the canvas.
        :type y: int
        :return: The closest cell.
        :rtype: Cell
        """
        col = x / (self.geometry.cell_width + self.geometry.column_padding)
        row = y / (self.geometry.cell_height + self.geometry.row_padding)
        return Cell(int(col), int(row))

    def set_geometry(self, width=None, height=None,
                     cell_width=None, cell_height=None,
                     column_padding=None, row_padding=None):
        """
        Request the grid's geometry (``Grid.geometry``) to be changed.

        Note that ``cell_width`` and ``cell_height`` have minimums, and, in the event that a requested change to them
        violates these minimums, they will be clamped greater than the minimums. The minimums are
        ``Grid.MIN_CELL_WIDTH`` and ``Grid.MIN_CELL_HEIGHT``.

        Also, ``width`` and ``height`` cannot be changed so as to "clip off" any ``DockableMixin``s on the grid.
        Therefore, once again, the ``width`` and ``height`` will be clamped to be greater than the minimum width and
        height of the grid state (``GridState.min_width`` and ``GridState.min_height``).

        To check if any of the requested new dimensions have been denied, consult the returned ``GridGeometry`` object,
        which contains the geometries actually deployed.

        :param width: The new width of the grid, or None for no change.
        :type width: int
        :param height: The new height of the grid, or None for no change.
        :type height: int
        :param cell_width: The new cell width of the grid, or None for no change.
        :type cell_width: int
        :param cell_height: The new cell height of the grid, or None for no change.
        :type cell_height: int
        :param column_padding: The new column padding of the grid, or None for no change.
        :type column_padding: int
        :param row_padding: The new row padding of the grid, or None for no change.
        :type row_padding: int
        :return: The new ``GridGeometry`` object.
        :rtype: GridGeometry
        """
        # Boolean to indicate if the dockables' geometries must be recalculated.
        invalid_dockable_geom = False
        if cell_width or cell_height or column_padding or row_padding:
            invalid_dockable_geom = True

        # Boolean to indicate if the grid state must be reconsidered.
        invalid_state_size = False
        if width or height:
            invalid_state_size = True

        # Since polling the min width and height is somewhat expensive, we only do it if a new width or height is
        # actually given.
        if width and width < self._grid_state.min_width:
            width = self._grid_state.min_width
        if height and height < self._grid_state.min_height:
            height = self._grid_state.min_height
        # Notice the use of "or" here so that width and height may not be zero by accident.
        width = width or self.geometry.width
        height = height or self.geometry.height

        cell_width = self._clamp(cell_width or self.geometry.cell_width, self.MIN_CELL_WIDTH)
        cell_height = self._clamp(cell_height or self.geometry.cell_height, self.MIN_CELL_HEIGHT)

        # Notice the none checks instead of simply "or": the paddings are allow to be zero.
        column_padding = self.geometry.column_padding if column_padding is None else column_padding
        row_padding = self.geometry.row_padding if row_padding is None else row_padding

        self.orig_geometry = self.geometry = GridGeometry(width, height,
                                                          cell_width, cell_height,
                                                          column_padding, row_padding)
        self.resize_scroll_region(self.geometry.width * (self.geometry.cell_width + self.geometry.column_padding),
                                  self.geometry.height * (self.geometry.cell_height + self.geometry.row_padding))
        if invalid_state_size:
            self._update_state_size(width, height)
        if invalid_dockable_geom:
            self._update_dockable_geometry()
        return self.geometry

    def _update_state_size(self, width, height):
        """
        Update the size of the grid state to the given ``width`` and ``height``.

        Note that simply doing
        ::
            self._grid_state.resize(height, width)

        will not suffice since the data stored in the grid state gets disordered.

        :param width: The new width.
        :type width: int
        :param height: The new height.
        :type height: int
        """
        self._grid_state = GridState(width, height)
        # Repopulate the state with all the dockables.
        for dockable, (_, cell) in self._dockables.items():
            self._grid_state.populate(cell, dockable.col_span, dockable.row_span)

    def _update_dockable_geometry(self):
        """
        Update the geometry of each ``DockableMixin`` managed by this grid.
        """
        for dockable, (id_, cell) in self._dockables.items():
            bbox = self._calc_bbox(cell, dockable.col_span, dockable.row_span)
            # Reset the size.
            self.itemconfig(id_, width=bbox.w, height=bbox.h)
            old_x, old_y = self.coords(id_)
            # Reset the position.
            self.move(id_, bbox.x - old_x, bbox.y - old_y)

    def set_resize_protocol(self, protocol):
        """
        Set the resize protocol (``Grid.resize_protocol``) to the given one.

        :param protocol: The resize protocol to employ.
        """
        self.resize_protocol = protocol
        self.geometry = self.orig_geometry
        if self.resize_protocol == self.RESIZE_PROTO_NONE:
            self.unbind("<Configure>")
            if self._resize_after_id:
                # Cancel a resize callback, should one exist, since the changed resize_protocol would mess it up.
                self.after_cancel(self._resize_after_id)
                self._resize_after_id = None
            # Update the dockable geometry in case the protocol was change while the window is expanded.
            self._update_dockable_geometry()
        else:
            self.bind("<Configure>", self._resize_bind_callback)
            # Simulate a resize callback once in case the protocol was change while the window is expanded.
            self._resize_data = Size(self.winfo_width(), self.winfo_height())
            self._resize_after_callback()

    def set_highlight_visual(self, bd_width=None, bd_colour=None, fill=None):
        """
        Set one or more of the visual aspects of the highlighting effect.

        :param bd_width: The new border width, or None for no change.
        :param bd_colour: The new border colour, or None for no change.
        :param fill: The new fill colour, or None for no change.
        """
        bd_width = bd_width or self.highlight_visual.bd_width
        bd_colour = bd_colour or self.highlight_visual.bd_colour
        fill = fill or self.highlight_visual.fill
        self.highlight_visual = HighlightVisual(bd_width, bd_colour, fill)

    def set_grid_visual(self, width=None, colour=None):
        """
        Set one or more of the visual aspects of the grid effect.

        :param width: The new border width, or None for no change.
        :param colour: The new border colour, or None for no change.
        """
        width = width or self.grid_visual.width
        colour = colour or self.grid_visual.colour
        self.grid_visual = GridVisual(width, colour)

    def _draw_grid(self):
        """Draw the grid rectangles on the canvas. One rectangle is drawn for each cell."""
        # TODO: The grid rectangles needn't be redrawn every time; they could be cached and invalidated when geometry is reset.
        dx = self.geometry.cell_width + self.geometry.column_padding
        dy = self.geometry.cell_height + self.geometry.row_padding
        for x in range(0, self.geometry.width * dx, dx):
            for y in range(0, self.geometry.height * dy, dy):
                self.create_rectangle(x, y, x + self.geometry.cell_width, y + self.geometry.cell_height,
                                      width=self.grid_visual.width,
                                      outline=self.grid_visual.colour,
                                      fill="",
                                      tag=self.TAG_GRIDLINE)

    def _clear_grid(self):
        """Clear the grid lines on the canvas, should they exist."""
        self.delete(self.TAG_GRIDLINE)

    def _set_highlight(self, cell, col_span, row_span):
        """
        Draw a highlighting rectangle with its upper-left cell located at ``cell``, width in cells equal to
        ``col_span``, and height in cells equal to ``row_span``.

        :param cell: The top-left cell.
        :type cell: Cell
        :param col_span: The width in cells.
        :type col_span: int
        :param row_span: The height in cells.
        :type row_span: int
        """
        x, y, w, h = self._calc_bbox(cell, col_span, row_span)
        # Draw the rectangle. The +- constants on each coordinate was empirically determined to produce the best-looking
        # rectangle within the grid lines.
        self.create_rectangle(x + 2, y + 2, x + w - 1, y + h - 1,
                              width=self.highlight_visual.bd_width,
                              outline=self.highlight_visual.bd_colour,
                              fill=self.highlight_visual.fill,
                              tag=self.TAG_HIGHLIGHT)

    def _clear_highlight(self):
        """Clear the highlight rectangle on the canvas, should it exist."""
        self.delete(self.TAG_HIGHLIGHT)

    def _resize_bind_callback(self, event):
        """
        A callback for resize events. Instead of resetting the geometry (which is somewhat expensive) upon every resize
        event, we schedule a callback to ``Grid._resize_after_callback`` every ``Grid.RESIZE_UPDATE_DELAY``
        milliseconds, but cache the new width and height every resize event.

        :param event: The tk event object.
        """
        # TODO: Turn this caching functionality into a decorator so it may be reused?
        # Only schedule a callback if one isn't already scheduled (_resize_data is None when no callback is scheduled.)
        if not self._resize_data:
            self._resize_after_id = self.after(self.RESIZE_UPDATE_DELAY, self._resize_after_callback)
        # Always, however, update _resize_data with the new width and height from the event.
        self._resize_data = Size(event.width, event.height)

    def _resize_after_callback(self):
        """Called every ``Grid.RESIZE_UPDATE_DELAY`` if the user is actively changing the size of the parent window."""
        # Whether the geometry in the x direction should change.
        resize_x = self._should_resize_x()
        # Whether the geometry in the y direction should change.
        resize_y = self._should_resize_y()

        if resize_x or resize_y:
            w, h, cw, ch, cp, rp = self.orig_geometry

            if resize_x:
                if self.resize_protocol == self.RESIZE_PROTO_EXPAND_CELLS:
                    cw = self._resize_data.width // self.geometry.width
                # Note the greater than 1 check, which avoids ZeroDivisionErrors
                elif self.resize_protocol == self.RESIZE_PROTO_ADD_PADDING and self.geometry.width > 1:
                    cp = (self._resize_data.width - self.geometry.width * self.geometry.cell_width) \
                         // (self.geometry.width - 1)
                else:
                    self.set_resize_protocol(self.RESIZE_PROTO_NONE)
                    raise ValueError("invalid resize protocol; setting resize protocol to RESIZE_PROTO_NONE")

            if resize_y:
                if self.resize_protocol == self.RESIZE_PROTO_EXPAND_CELLS:
                    ch = self._resize_data.height // self.geometry.height
                # Note the greater than 1 check, which avoids ZeroDivisionErrors
                elif self.resize_protocol == self.RESIZE_PROTO_ADD_PADDING and self.geometry.height > 1:
                    rp = (self._resize_data.height - self.geometry.height * self.geometry.cell_height) \
                         // (self.geometry.height - 1)
                else:
                    self.set_resize_protocol(self.RESIZE_PROTO_NONE)
                    raise ValueError("invalid resize protocol; setting resize protocol to RESIZE_PROTO_NONE")

            self.geometry = GridGeometry(w, h, cw, ch, cp, rp)
            self._update_dockable_geometry()
        # If neither the x or y directions need to be changed according to the window size, make sure the orig_geometry
        # (i.e. the geometry originally set manually by the user) is in use.
        elif self.geometry != self.orig_geometry:
            self.geometry = self.orig_geometry
            self._update_dockable_geometry()

        # Set _resize_data to None to indicate that the data in it has been applied to the grid's geometry and now a new
        # callback to this method may be scheduled.
        self._resize_data = None

    def _should_resize_x(self):
        """
        :return: Whether the grid should be resized in the x direction in accordance with the window size.
        """
        # The x scroll bar will be maxed out if the space allocated to the grid is greater than the width of the
        # scrollregion, and hence this may be used as an indicator for when the grid should be resized in the x
        # direction in accordance with the window size.
        return self.x_scrollbar.get() == self.MAX_SCROLLBAR_POS

    def _should_resize_y(self):
        """
        :return: Whether the grid should be resized in the y direction in accordance with the window size.
        """
        # The y scroll bar will be maxed out if the space allocated to the grid is greater than the height of the
        # scrollregion, and hence this may be used as an indicator for when the grid should be resized in the y
        # direction in accordance with the window size.
        return self.y_scrollbar.get() == self.MAX_SCROLLBAR_POS

    @staticmethod
    def _contained_in(query_cell, containing_cell, col_span, row_span):
        """
        Check whether ``query_cell`` is contained in the rectangle described by ``containing_cell``, ``col_span``,
        and ``row_span``.

        :param query_cell: The cell to check for containment in the rectangle.
        :type query_cell: Cell
        :param containing_cell: The top-left cell in the rectangle.
        :type containing_cell: Cell
        :param col_span: The width in cells of the rectangle.
        :type col_span: int
        :param row_span: The height in cells of the rectangle.
        :type row_span: int
        :return: Whether ``query_cell`` is in the rectangle described by the given information.
        :rtype: bool
        """
        col, row = query_cell
        ccol, crow = containing_cell
        return col in range(ccol, ccol + col_span) and row in range(crow, crow + row_span)

    @staticmethod
    def _clamp(n, min_):
        """
        Helper method to clamp a positive number ``n`` to greater than ``min_``.

        :param n: The number to clamp.
        :param min_: The lower bound on n.
        :return: The clamped number.
        """
        return n if n >= min_ else min_


class Window(style.Toplevel):
    """
    A wrapper around a tkinter Toplevel. This class's main importance lies in the fact that it contains the ``Grid``
    instance.
    """

    def __init__(self, root, width, height, *args, **kwargs):
        """
        :param root: The parent tkinter widget for the Toplevel.
        :param width: The width of the grid.
        :type width: int
        :param height: The height of the grid.
        :type height: int
        :param args: Additional args for the ``Grid`` constructor.
        :param kwargs: Additional kwargs for the ``Grid`` constructor.
        """
        super().__init__(root, style=kwargs.get("style"))

        self.grid = Grid(self, width, height, *args, **kwargs)
        self.grid.frame.pack(fill=tk.BOTH, expand=True)


class DockableMixin:
    """
    A mixin class designed to be used with the tkinter widget classes.

    This class provides all the foundation for a widget to become "dockable" on a ``Grid``. Namely, this classes binds
    to the right click, right click release, and right click motion events as the means to drag each ``DockableMixin``
    widget to snap to different locations on the grid. Therefore, subclasses mustn't also bind to the right click
    events.

    In the situation that a subclass is a container widget (e.g. a ``tkinter.Frame``) and it is desirable that specific
    children "relay" right click events to the ``DockableMixin`` parent, the ``DockableMixin.bind_drag_on`` method is
    provided to bind said specific widgets with appropriate right click events. Also, ``DockableMixin.unbind_drag_on``
    is provided to remove any bindings on a particular widget which has been bound through
    ``DockableMixin.bind_drag_on`` already.

    If one wishes to programmatically (as opposed to through the gui) change a dockable's size or position, use the
    ``DockableMixin.resize_dockable`` or ``DockableMixin.move_dockable`` methods, respectively.
    """

    # TODO: Make dockables relay scroll events to grid

    def __init__(self, parent_grid, col_span, row_span, *args, **kwargs):
        """
        :param parent_grid: The tkinter parent for this widget. As the parameter name suggests, it should be a ``Grid``.
        :type parent_grid: Grid
        :param col_span: The column span (width) this dockable shall consume on its containing grid.
        :type col_span: int
        :param row_span: The row span (height) this dockable shall consume on its containing grid.
        :type row_span: int
        :param args: Args for the tkinter widget constructor.
        :param kwargs: Kwargs for the tkinter widget constructor.
        """
        super().__init__(parent_grid, *args, **kwargs)

        self.parent_grid = parent_grid
        self.col_span = col_span
        self.row_span = row_span

        self.bind_drag_on(self)

    def move_dockable(self, col, row):
        """
        Move this dockable to the given location. If moving the dockable to the specified location would result in a
        grid conflict, the move will fail and no changes will be made.

        :param col: The column to move the dockable to.
        :type col: int
        :param row: The row to move the dockable to.
        :type row: int
        :return: Whether or not the move was successful.
        :rtype: bool
        """
        return self.parent_grid.move_dockable(self, Cell(col, row))

    def resize_dockable(self, col_span=None, row_span=None):
        """
        Resize the dockable to the given column and row spans (i.e. width and height, respectively). If the resize would
        result in a grid conflict with the dockable in its current location, the dockable will be moved to the nearest
        location in which it can "fit". If such a location does not exist, the grid will be expanded as needed to
        accommodate the dockable.

        :param col_span: The new column span (width) of the dockable, or None for no change.
        :type col_span: int
        :param row_span: The new row span (height) of the dockable, or None for no change.
        :type row_span: int
        """
        self.col_span = col_span or self.col_span
        self.row_span = row_span or self.row_span
        self.parent_grid.dockable_resized(self)

    def bind_drag_on(self, widget):
        """
        Bind the three right click events associated with dragging dockables (click, release, and motion) to the given
        widget.

        :param widget: The widget to bind the right click events to.
        """
        # lambdas are used here to ignore the event objects passed by tkinter.
        widget.bind("<Button-3>", lambda _: self.parent_grid.signal_drag_start(self))
        widget.bind("<ButtonRelease-3>", lambda _: self.parent_grid.signal_drag_stop())
        widget.bind("<B3-Motion>", lambda _: self.parent_grid.signal_drag_motion())

    @staticmethod
    def unbind_drag_on(widget):
        """
        Unbind the three right click events associated with dragging dockables (click, release, and motion) from the
        given widget.

        :param widget: The widget to unbind the right click events from.
        """
        widget.unbind("<Button-3>")
        widget.unbind("<ButtonRelease-3>")
        widget.unbind("<B3-Motion>")


class GuiManager:
    """
    Manages the tkinter root (``tkinter.Tk``) object and the creation and destruction of windows. This class also
    provides an asynchronous version of the tkinter mainloop.
    """

    def __init__(self, prog_name):
        """
        :param prog_name: The name to associate with the gui. This will be used in the title of all windows.
        :type prog_name: str
        """
        self.root = tk.Tk()
        # Withdraw the root window from the screen, making it invisible.
        self.root.withdraw()
        self.prog_name = prog_name

        self.windows = {}
        """
        A dictionary associating an integer (key) to each window (value). This is the integer displayed in each window's
        title.
        """

    async def async_mainloop(self, interval):
        """
        An asynchronous version of the tkinter mainloop. This works by updating the tkinter root and then yielding
        execution for the given interval.

        If a ``tkinter.TclError`` occurs, it is printed out and the loop is broken.

        :param interval: How long to sleep for (in milliseconds) in between updates.
        :type interval: int
        """
        # Convert interval from milliseconds to seconds.
        interval /= 1000
        try:
            while True:
                self.root.update()
                await asyncio.sleep(interval)
        except tk.TclError as e:
            print("Tkinter error occurred:\n" + str(e))  # TODO: Temp?

    def new_win(self, width, height, *args, **kwargs):
        """
        Create and return a new ``Window``. The window is automatically given a title consisting of the
        ``GuiManager.prog_name`` and its unique window number (integer), starting at one.

        :param width: The width of the grid of the window.
        :type width: int
        :param height: The height of the grid of the window.
        :type height: int
        :param args: Additional args for the ``Window`` constructor.
        :param kwargs: Additional kwargs for the ``Window`` constructor.
        :return: The new window.
        :rtype: Window
        """
        win = Window(self.root, width, height, *args, **kwargs)
        num = self._get_next_win_num()
        win.title(self.prog_name + " ({})".format(num))
        self.windows[num] = win
        return win

    def _get_next_win_num(self):
        """
        Generate a unique window number (integer), starting at one.

        :return: The generated integer.
        :rtype: int
        """
        n = 1
        while n in self.windows:
            n += 1
        return n

    def destroy_win(self, n):
        """
        Destroy the given window by its identifying number.

        :param n: The to-be-destroyed window's number.
        :type n: int
        """
        self.windows.pop(n).destroy()
