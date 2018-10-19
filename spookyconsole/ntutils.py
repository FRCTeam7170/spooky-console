
"""
TODO
"""

import click
import pycmds
from pycmds.utils import DotDict
from networktables.networktables import NetworkTables


TRUE = ["true", "t"]
FALSE = ["false", "f"]
BOOLEAN_CONV_FAIL_MSG = "cannot convert {!r} to boolean"
DOUBLE_CONV_FAIL_MSG = "cannot convert {!r} to double"


def assure_ntpath_exists(ctx):
    if isinstance(ctx.obj, DotDict) and "nt_current_path" not in ctx.obj:
        ctx.obj["nt_current_path"] = "/"


def str_to_bool(string):
    string = string.lower()
    if string in TRUE:
        return True
    elif string in FALSE:
        return False
    else:
        raise ValueError(BOOLEAN_CONV_FAIL_MSG.format(string))


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
            ret = ctx.obj["nt_current_path"]
            ret += NetworkTables.PATH_SEPARATOR if not ret.endswith(NetworkTables.PATH_SEPARATOR) else ""
        for component in self.path.split(NetworkTables.PATH_SEPARATOR):
            if component == self.CURR_DIR:
                continue
            elif component == self.PREV_DIR:
                if ret != "/":
                    ret = ret[len(ret) - ret[-2::-1].index(NetworkTables.PATH_SEPARATOR) - 1]
            else:
                ret += component + NetworkTables.PATH_SEPARATOR
        return ret

    @staticmethod
    def assert_valid_name(name):
        if any((len(x) == 0 for x in name.split(NetworkTables.PATH_SEPARATOR))):
            raise ValueError("invalid NT path name")


class NTPathParamType(click.ParamType):

    def convert(self, value, param, ctx):
        assure_ntpath_exists(ctx)
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


BOOLEAN_ARRAY = BooleanArrayParamType("[]")
DOUBLE_ARRAY = DoubleArrayParamType("[]")
STRING_ARRAY = pycmds.LIST

NT_PATH = NTPathParamType()
NT_ENTRY = NTEntryParamType()
NT_TABLE = NTTableParamType()
