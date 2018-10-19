
"""
TODO
"""

from collections import namedtuple
from .utils import find_nth
from .exceptions import TableFormatError


def is_numeric(data):
    return isinstance(data, (int, float, complex))


TableStyle = namedtuple("TableStyle", (
    "top_left_corner", "top_right_corner", "bottom_right_corner", "bottom_left_corner",
    "top_t", "right_t", "bottom_t", "left_t",
    "vert", "horz", "junction",
    "header_top_t", "header_right_t", "header_bottom_t", "header_left_t",
    "header_horz", "header_vert"
))


class Align:

    def align(self, data, width, height):
        raise NotImplementedError("{} class 'align' method must be overridden.".format(self.__class__.__name__))


class CenterAlign(Align):

    def align(self, data, width, height):
        pass


CENTER_ALIGN = CenterAlign()

TableCoordinate = namedtuple("TableCoordinates", ("x", "y"))


class TableEntry:

    def __init__(self, data, align, top_left_coord, bottom_right_coord):
        self.data = data
        self.align = align
        self.coords = (top_left_coord, bottom_right_coord)

    @property
    def row_span(self):
        return self.coords[1].x - self.coords[0].x + 1

    @property
    def col_span(self):
        return self.coords[1].y - self.coords[0].y + 1


class TableRow:

    def __init__(self, row_num, height=None, num_cols=None):
        self.row_num = row_num
        self.entries = []
        self.col_idx = 0
        self.num_cols = num_cols
        self.row_height = height or 1
        self.strict_height = height is not None

    def __str__(self):
        pass

    def __call__(self, *args, **kwargs):
        return self.insert(*args, **kwargs)

    def skip(self, num_col=1):
        for i in range(num_col):
            self.insert("")

    def insert(self, data, align=CENTER_ALIGN, row_span=1, col_span=1):
        # TODO: make sure based on row and col span and previous entries that an entry can be placed
        if row_span < 1 or col_span < 1:
            raise ValueError("row and column spans must be at least 1")
        if self.num_cols is not None and self.col_idx + col_span > self.num_cols:
            raise TableFormatError("table restricted to {} columns".format(self.num_cols))
        self.col_idx += col_span

        lines_consumed = data.count("\n") + 1
        if lines_consumed > self.row_height:
            if self.strict_height:
                data = data[:find_nth(data, "\n", self.row_height - 1)]
            else:
                self.row_height = lines_consumed

        self.entries.append(TableEntry(data, align, *self.get_coords(row_span, col_span)))

    def get_coords(self, row_span, col_span):
        return TableCoordinate(self.row_num, self.col_idx),\
               TableCoordinate(self.row_num + row_span - 1, self.col_idx + col_span - 1)


class Table:

    GROW_ROW = -1

    def __init__(self, width=GROW_ROW, style="fancy_grid"):
        pass

    def __str__(self):
        pass

    def row(self):
        pass

    def header(self):
        pass
