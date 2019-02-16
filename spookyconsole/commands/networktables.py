
"""
TODO
"""

from collections import namedtuple
import click
import pycmds
from networktables.networktables import NetworkTables
from networktables.instance import NetworkTablesInstance
import tabulate
from spookyconsole.nt import ntutils


@click.group(cls=pycmds.AliasGroup)
@click.pass_context
def nt(ctx):
    ctx.obj.setdefault("nt_path", "/")


@click.command()
@click.argument("entry", type=ntutils.NT_ENTRY_TYPE)
def get(entry):
    return entry.value


@click.command("set")
@click.option("kind", "--boolean", flag_value=NetworkTablesInstance.EntryTypes.BOOLEAN)
@click.option("kind", "--double", flag_value=NetworkTablesInstance.EntryTypes.DOUBLE)
@click.option("kind", "--string", flag_value=NetworkTablesInstance.EntryTypes.STRING, default=True)
@click.option("kind", "--boolean-array", flag_value=NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY)
@click.option("kind", "--double-array", flag_value=NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY)
@click.option("kind", "--string-array", flag_value=NetworkTablesInstance.EntryTypes.STRING_ARRAY)
@click.argument("entry", type=ntutils.NT_ENTRY_TYPE)
@click.argument("value")
@click.pass_context
def set_(ctx, entry, value, kind):
    print(f"entry: {entry},{type(entry)}; value: {repr(value)},{type(value)}; kind: {kind},{type(kind)}")
    return ntutils.set_entry_by_type(entry, ntutils.type_cast(value, kind, ctx))


@click.command()
@click.argument("path", type=ntutils.NT_PATH_TYPE)
@click.pass_context
def cd(ctx, path):
    ctx.obj.nt_path = path


@click.command()
@click.pass_context
def pwd(ctx):
    return ctx.obj.nt_path


ListElement = namedtuple("ListElement", ("is_entry", "key", "parent"))
list_aliases = ["ls", "dir"]


@click.command("list")
@click.argument("path", type=ntutils.NT_PATH_TYPE, required=False)
@click.option("recurse", "--recurse/--no-recurse", "-r/ ", default=False)
@click.option("output", "--tables", "-t", flag_value="tables")
@click.option("output", "--entries", "-e", flag_value="entries")
@click.option("output", "--both", flag_value="both", default=True)
@click.option("value", "--value/--no-value", "-v/ ", default=False)
@click.option("kind", "--type/--no-type", "-T/ ", default=False)
@click.pass_context
def list_(ctx, path, recurse, output, value, kind):
    if path is None:
        path = ctx.obj.nt_path

    find_entries = output in ("entries", "both")
    find_tables = output in ("tables", "both")
    table = NetworkTables.getTable(path)
    items = []
    if find_entries:
        items.extend((ListElement(True, key, table) for key in table.getKeys()))
    if find_tables or recurse:
        items.extend((ListElement(False, key, table) for key in table.getSubTables()))
    if recurse:
        for item in items:
            if item.is_entry:
                continue
            subtable = item.parent.getSubTable(item.key)
            if find_entries:
                items.extend((ListElement(True, key, subtable) for key in subtable.getKeys()))
            items.extend((ListElement(False, key, subtable) for key in subtable.getSubTables()))

    item_type_column = output == "both"

    header = []
    if item_type_column:
        header.append("Table/Entry")
    header.append("Path")
    if kind:
        header.append("Type")
    if value:
        header.append("Value")

    content = []
    for item in items:
        row = []
        if item.is_entry and find_entries:
            if item_type_column:
                row.append("E")
            row.append(item.key)
            if value:
                row.append(item.parent.getEntry(item.key).value)
            if kind:
                row.append(ntutils.type_constant_to_str(item.parent.getEntry(item.key).type))
        elif find_tables:
            if item_type_column:
                row.append("T")
            row.append(item.key)
            if find_entries:
                row.extend([""] * (value + kind))
        content.append(row)

    return tabulate.tabulate(content, header, tablefmt="fancy_grid")


@click.command()
@click.option("team", "--team", "-t", default=False)
@click.argument("server")
@click.pass_context
def connect(ctx, team, server):
    if team:
        try:
            NetworkTables.startClientTeam(int(server))
        except ValueError:
            raise click.BadParameter("could not convert given server into a team number", ctx, "server")
    else:
        NetworkTables.startClient(server)
