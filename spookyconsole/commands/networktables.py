
"""
TODO
"""

from collections import namedtuple
import click
from networktables.networktables import NetworkTables
import tabulate
from .. import ntutils


_BOOLEAN = 0
_DOUBLE = 1
_STRING = 2
_RAW = 3
_BOOLEAN_ARRAY = 4
_DOUBLE_ARRAY = 5
_STRING_ARRAY = 6


@click.group()
@click.pass_context
def nt(ctx):
    ntutils.assure_ntpath_exists(ctx)


@click.command()
@click.argument("entry", type=ntutils.NT_ENTRY)
def get(entry):
    return entry.value


@click.command("set")
@click.option("kind", "--boolean", flag_value=_BOOLEAN)
@click.option("kind", "--double", flag_value=_DOUBLE)
@click.option("kind", "--string", flag_value=_STRING, default=True)
@click.option("kind", "--boolean-array", flag_value=_BOOLEAN_ARRAY)
@click.option("kind", "--double-array", flag_value=_DOUBLE_ARRAY)
@click.option("kind", "--string-array", flag_value=_STRING_ARRAY)
@click.argument("entry", type=ntutils.NT_ENTRY)
@click.argument("value")
@click.pass_context
def set_(ctx, entry, value, kind):
    if kind == _BOOLEAN:
        try:
            value = ntutils.str_to_bool(value)
        except ValueError as e:
            raise click.BadParameter(str(e))
        return entry.setBoolean(value)
    elif kind == _DOUBLE:
        try:
            value = float(value)
        except ValueError:
            raise click.BadParameter(ntutils.DOUBLE_CONV_FAIL_MSG.format(value))
        return NetworkTables.getEntry(entry).setDouble(value)
    elif kind == _STRING:
        return NetworkTables.getEntry(entry).setString(value)
    elif kind == _BOOLEAN_ARRAY:
        # TODO: manual invocation of convert seems a little hacky...
        value = ntutils.BOOLEAN_ARRAY.convert(value, None, ctx)
        return NetworkTables.getEntry(entry).setBooleanArray(value)
    elif kind == _DOUBLE_ARRAY:
        value = ntutils.DOUBLE_ARRAY.convert(value, None, ctx)
        return NetworkTables.getEntry(entry).setDoubleArray(value)
    else:  # kind == _STRING_ARRAY
        value = ntutils.STRING_ARRAY.convert(value, None, ctx)
        return NetworkTables.getEntry(entry).setStringArray(value)


@click.command()
@click.argument("path", type=ntutils.NT_PATH)
@click.pass_context
def cd(ctx, path):
    ctx.obj["nt_current_path"] = path


@click.command()
@click.pass_context
def pwd(ctx):
    return ctx.obj["nt_current_path"]


ListElement = namedtuple("ListElement", ("is_entry", "key", "parent"))
list_aliases = ["ls", "dir"]


@click.command("list")
@click.argument("path", type=ntutils.NT_PATH, required=False)
@click.option("recurse", "--recurse/--no-recurse", "-r/ ", default=False)
@click.option("output", "--tables", "-t", flag_value="tables")
@click.option("output", "--entries", "-e", flag_value="entries")
@click.option("output", "--both", flag_value="both", default=True)
@click.option("value", "--value/--no-value", "-v/ ", default=False)
@click.option("kind", "--type/--no-type", "-T/ ", default=False)
@click.pass_context
def list_(ctx, path, recurse, output, value, kind):

    if path is None:
        path = ctx.obj["nt_current_path"]
    else:
        path = ntutils.NTPath(path).resolve_full_name(ctx)

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
def monitor():
    pass
