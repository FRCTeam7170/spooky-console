
from networktables.instance import NetworkTablesInstance
import random


class TableSim:

    class EntrySim:

        def __init__(self, key, value):
            self.key = key
            self.value = value
            self.type = random.choice([NetworkTablesInstance.EntryTypes.BOOLEAN,
                                       NetworkTablesInstance.EntryTypes.DOUBLE,
                                       NetworkTablesInstance.EntryTypes.STRING,
                                       NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY,
                                       NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY,
                                       NetworkTablesInstance.EntryTypes.STRING_ARRAY])

        def getName(self):
            return self.key

        def getType(self):
            return self.type

        def setBoolean(self, val):
            self.value = val

        setDouble = setString = setBooleanArray = setDoubleArray = setStringArray = setBoolean

    PATH_SEPARATOR = '/'

    def __init__(self, data, path=PATH_SEPARATOR):
        self.data = data
        self.path = path

        for k, v in self.data.items():
            if not self.is_sub_table(v) and not self.is_entry(v):
                self.data[k] = self.EntrySim(k, v)

    def getEntry(self, key):
        ret = self.data[key]
        assert self.is_entry(ret)
        return ret

    def getSubTable(self, key):
        ret = self.data[key]
        assert self.is_sub_table(ret)
        return TableSim(ret, self.path + key + self.PATH_SEPARATOR)

    def getKeys(self):
        return [key for key, value in self.data.items() if isinstance(value, TableSim.EntrySim)]

    def getSubTables(self):
        return [key for key, value in self.data.items() if isinstance(value, dict)]

    def containsKey(self, key):
        try:
            return isinstance(self.data[key], TableSim.EntrySim)
        except KeyError:
            return False

    def containsSubTable(self, key):
        try:
            return isinstance(self.data[key], dict)
        except KeyError:
            return False

    @staticmethod
    def is_sub_table(data):
        return isinstance(data, dict)

    @staticmethod
    def is_entry(data):
        return isinstance(data, TableSim.EntrySim)
