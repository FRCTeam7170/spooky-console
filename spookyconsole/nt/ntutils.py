
"""
TODO
"""

import click
import pycmds
from networktables.instance import NetworkTablesInstance
from networktables.networktables import NetworkTables


TRUE = ["true", "t"]
FALSE = ["false", "f"]
BOOLEAN_CONV_FAIL_MSG = "cannot convert {!r} to boolean"
DOUBLE_CONV_FAIL_MSG = "cannot convert {!r} to double"


def str_to_bool(string):
    lstring = string.lower().strip()
    if lstring in TRUE:
        return True
    elif lstring in FALSE:
        return False
    else:
        raise ValueError(BOOLEAN_CONV_FAIL_MSG.format(string))


def type_constant_to_str(kind):
    if kind == NetworkTablesInstance.EntryTypes.BOOLEAN:
        return "BOOLEAN"
    elif kind == NetworkTablesInstance.EntryTypes.DOUBLE:
        return "DOUBLE"
    elif kind == NetworkTablesInstance.EntryTypes.STRING:
        return "STRING"
    elif kind == NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
        return "BOOLEAN_ARRAY"
    elif kind == NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
        return "DOUBLE_ARRAY"
    else:  # kind == NetworkTablesInstance.EntryTypes.STRING_ARRAY:
        return "STRING_ARRAY"


def type_cast(value, kind, ctx=None):
    try:
        if kind == NetworkTablesInstance.EntryTypes.BOOLEAN:
            return str_to_bool(value)
        elif kind == NetworkTablesInstance.EntryTypes.DOUBLE:
            try:
                return float(value)
            except ValueError:
                raise ValueError(DOUBLE_CONV_FAIL_MSG.format(value))
        elif kind == NetworkTablesInstance.EntryTypes.STRING:
            return value
        elif kind == NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
            # TODO: manual invocation of convert seems a little hacky...
            return BOOLEAN_ARRAY_TYPE.convert(value, None, ctx)
        elif kind == NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
            return DOUBLE_ARRAY_TYPE.convert(value, None, ctx)
        else:  # kind == NetworkTablesInstance.EntryTypes.STRING_ARRAY
            return STRING_ARRAY_TYPE.convert(value, None, ctx)
    except click.BadParameter as e:
        raise ValueError(e)


def set_entry_by_type(entry, value):
    kind = entry.getType()
    if kind == NetworkTablesInstance.EntryTypes.BOOLEAN:
        return entry.setBoolean(value)
    elif kind == NetworkTablesInstance.EntryTypes.DOUBLE:
        return entry.setDouble(value)
    elif kind == NetworkTablesInstance.EntryTypes.STRING:
        return entry.setString(value)
    elif kind == NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
        return entry.setBooleanArray(value)
    elif kind == NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
        return entry.setDoubleArray(value)
    else:  # kind == NetworkTablesInstance.EntryTypes.STRING_ARRAY
        return entry.setStringArray(value)


class NTPath:

    CURR_DIR = "."
    PREV_DIR = ".."

    def __init__(self, string_path):
        self.assert_valid_name(string_path)
        self.path = string_path

    @property
    def is_absolute(self):
        return self.path.startswith(NetworkTables.PATH_SEPARATOR)

    @property
    def is_relative(self):
        return not self.is_absolute

    def resolve_full_name(self, ctx):
        if self.is_absolute:
            ret = ""
        else:
            ret = ctx.obj.nt_path
            if not ret.endswith(NetworkTables.PATH_SEPARATOR):
                ret += NetworkTables.PATH_SEPARATOR
        for component in self.path.split(NetworkTables.PATH_SEPARATOR):
            if component == self.CURR_DIR:
                continue
            elif component == self.PREV_DIR:
                if ret != "/":
                    ret = ret[:(len(ret) - ret[-2::-1].index(NetworkTables.PATH_SEPARATOR) - 1)]
            else:
                ret += component + NetworkTables.PATH_SEPARATOR
        return ret[:-1] if ret.endswith(NetworkTables.PATH_SEPARATOR) else ret

    @staticmethod
    def assert_valid_name(name):
        if any((len(x) == 0 for x in name.split(NetworkTables.PATH_SEPARATOR))):
            raise ValueError("invalid NT path name")


class NTPathParamType(click.ParamType):

    def convert(self, value, param, ctx):
        try:
            return NTPath(value).resolve_full_name(ctx)
        except ValueError as e:
            self.fail(str(e), param, ctx)


class NTEntryParamType(NTPathParamType):

    def convert(self, value, param, ctx):
        return NetworkTables.getEntry(super().convert(value, param, ctx))


class NTTableParamType(NTPathParamType):

    def convert(self, value, param, ctx):
        return NetworkTables.getTable(super().convert(value, param, ctx))


class BooleanArrayParamType(pycmds.ListParamType):

    def item_hook(self, item):
        try:
            return str_to_bool(item)
        except ValueError as e:
            self.fail(str(e))


class DoubleArrayParamType(pycmds.ListParamType):

    def item_hook(self, item):
        try:
            return float(item)
        except ValueError:
            self.fail(DOUBLE_CONV_FAIL_MSG.format(item))


BOOLEAN_ARRAY_TYPE = BooleanArrayParamType("[]")
DOUBLE_ARRAY_TYPE = DoubleArrayParamType("[]")
STRING_ARRAY_TYPE = pycmds.LIST

NT_PATH_TYPE = NTPathParamType()
NT_ENTRY_TYPE = NTEntryParamType()
NT_TABLE_TYPE = NTTableParamType()
