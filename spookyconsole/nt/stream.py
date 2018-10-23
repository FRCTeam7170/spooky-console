
from collections import deque
import typing
from networktables.instance import NetworkTablesInstance
from spookyconsole.nt import ntutils


class NTStream:

    def __init__(self, kind, receiving_entry=None, transmitting_entry=None, cache_size=100):
        if not (receiving_entry or transmitting_entry):
            raise ValueError("at least one entry must be given")
        self.r_set_func = None
        self.t_set_func = None
        self.receiving_entry = receiving_entry
        self.transmitting_entry = transmitting_entry
        if receiving_entry:
            self.r_set_func = self._check_entry_type(receiving_entry, kind)
        if transmitting_entry:
            self.t_set_func = self._check_entry_type(transmitting_entry, kind)
            self.cache = deque(maxlen=cache_size)

    def read(self):
        if not self.readable():
            raise ValueError("cannot read a write-only stream")
        ret = []
        if self._data_available():
            ret = self.receiving_entry.value
            self.r_set_func([])
        return ret

    def write(self, data):
        if not self.writeable():
            raise ValueError("cannot write to a read-only stream")
        if not isinstance(data, typing.Container):
            data = [data]
        self.flush()
        self.cache.extend(data)
        self.flush()

    def readable(self):
        return self.r_set_func is not None

    def writeable(self):
        return self.t_set_func is not None

    def _data_available(self):
        return bool(self.receiving_entry.value)

    def _output_blocked(self):
        return bool(self.transmitting_entry.value)

    def flush(self):
        if not self.writeable():
            raise ValueError("cannot write to a read-only stream")
        if not self._output_blocked():
            self.t_set_func(list(self.cache))
            self.cache.clear()

    @staticmethod
    def _check_entry_type(entry, kind):
        entry_kind = entry.getType() if entry.exists() else None
        if kind in (NetworkTablesInstance.EntryTypes.BOOLEAN, NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY):
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
                NTStream._error(entry_kind, kind)
            else:
                entry.setBooleanArray([])
            return entry.setBooleanArray
        elif kind in (NetworkTablesInstance.EntryTypes.DOUBLE, NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY):
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
                NTStream._error(entry_kind, kind)
            else:
                entry.setDoubleArray([])
            return entry.setDoubleArray
        else:  # kind in (NetworkTablesInstance.EntryTypes.STRING, NetworkTablesInstance.EntryTypes.STRING_ARRAY)
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.STRING_ARRAY:
                NTStream._error(entry_kind, kind)
            else:
                entry.setStringArray([])
            return entry.setStringArray

    @staticmethod
    def _error(entry_kind, kind):
        entry_kind = ntutils.type_constant_to_str(entry_kind)
        kind = ntutils.type_constant_to_str(kind)
        raise TypeError("entry type ({}) and given data type ({}) conflict".format(entry_kind, kind))
