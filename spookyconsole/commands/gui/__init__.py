
"""
TODO
"""

import asyncio
import click
from pycmds.utils import DotDict
from spookyconsole.gui import core


def _create_gui_manager(prog_name, interval):
    manager = core.GuiManager(prog_name)
    asyncio.create_task(manager.async_mainloop(interval))
    return manager


class WinNumParamType(click.ParamType):

    def convert(self, value, param, ctx):
        if value == -1:
            sel_win = ctx.obj.gui.sel_win
            if sel_win in ctx.obj.gui.manager.windows:
                return sel_win
            else:
                self.fail("selected window is invalid", param, ctx)
        else:
            if value in ctx.obj.gui.manager.windows:
                return value
            else:
                self.fail("given window number is invalid", param, ctx)


class GridParamType(WinNumParamType):

    def convert(self, value, param, ctx):
        return ctx.obj.gui.manager.windows[super().convert(value, param, ctx)].grid


WIN_NUM_TYPE = WinNumParamType()
GRID_TYPE = GridParamType()


@click.group()
@click.pass_context
def gui(ctx):
    if "gui" not in ctx.obj:
        ctx.obj.gui = DotDict(dynamic=False)
    if "manager" not in ctx.obj.gui:
        try:
            ctx.obj.gui.manager = _create_gui_manager(ctx.obj.prog_name, ctx.obj.gui_interval)
        except KeyError as e:
            ctx.fail(str(e))
    ctx.obj.gui.setdefault("sel_win", 0)


@click.command()
@click.option("width", "--width", "-w", type=int, default=5)
@click.option("height", "--height", "-h", type=int, default=5)
@click.pass_context
def new(ctx, width, height):
    # TODO: more options for grid?
    return ctx.obj.gui.manager.new_win(width, height)[1]


destroy_aliases = ["remove", "del", "delete"]


@click.command()
@click.argument("window", type=WIN_NUM_TYPE)
@click.pass_context
def destroy(ctx, window):
    ctx.obj.gui.manager.destroy_win(window)


select_aliases = ["sel"]


@click.command()
@click.argument("window", type=WIN_NUM_TYPE)
@click.pass_context
def select(ctx, window):
    ctx.obj.gui.sel_win = window


# TODO: styling
# TODO: dockable management
