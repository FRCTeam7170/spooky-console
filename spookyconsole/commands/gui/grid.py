
"""
TODO
"""

import tkinter as tk
import click
from spookyconsole.commands.gui import WIN_NUM_TYPE, GRID_TYPE
from spookyconsole.gui import core as gui_core


class TkinterColourParamType(click.ParamType):

    def convert(self, value, param, ctx):
        if not self._is_valid_colour(ctx, value):
            self.fail("{} is not a valid tkinter colour".format(value), param, ctx)
        return value

    @staticmethod
    def _is_valid_colour(ctx, colour):
        root = ctx.obj.gui.manager.root
        try:
            tk.Button(root, bg=colour).destroy()
            return True
        except tk.TclError:
            return False


TKINTER_COLOUR_TYPE = TkinterColourParamType()


@click.group()
def grid():
    pass


geometry_aliases = ["geom"]


@click.command()
@click.option("grid", "--grid", "-g", type=GRID_TYPE)
@click.option("width", "--width", "-w", type=int)
@click.option("height", "--height", "-h", type=int)
@click.option("cell_width", "--cell-width", "-W", type=int)
@click.option("cell_height", "--cell-height", "-H", type=int)
@click.option("column_padding", "--column-padding", "-c", type=int)
@click.option("row_padding", "--row-padding", "-r", type=int)
def geometry(grid, width, height, cell_width, cell_height, column_padding, row_padding):
    grid.set_geometry(width, height, cell_width, cell_height, column_padding, row_padding)


resize_proto_aliases = ["rp"]


@click.command()
@click.option("grid", "--grid", "-g", type=GRID_TYPE)
@click.option("rp", "--none", flag_value=gui_core.Grid.RESIZE_PROTO_NONE)
@click.option("rp", "--cells", flag_value=gui_core.Grid.RESIZE_PROTO_EXPAND_CELLS, default=True)
@click.option("rp", "--padding", flag_value=gui_core.Grid.RESIZE_PROTO_ADD_PADDING)
def resize_proto(grid, rp):
    grid.set_resize_protocol(rp)


highlight_visual_aliases = ["hv"]


@click.command()
@click.option("grid", "--grid", "-g", type=GRID_TYPE)
@click.option("bd_width", "--bd-width", "-w", type=int)
@click.option("bd_colour", "--bd-colour", "-c", type=TKINTER_COLOUR_TYPE)
@click.option("fill", "--fill", "-f", type=TKINTER_COLOUR_TYPE)
def highlight_visual(grid, bd_width, bd_colour, fill):
    grid.set_highlight_visual(bd_width, bd_colour, fill)


grid_visual_aliases = ["gv"]


@click.command()
@click.option("grid", "--grid", "-g", type=GRID_TYPE)
@click.option("width", "--width", "-w", type=int)
@click.option("colour", "--colour", "-c", type=TKINTER_COLOUR_TYPE)
def grid_visual(grid, width, colour):
    grid.set_grid_visual(width, colour)
