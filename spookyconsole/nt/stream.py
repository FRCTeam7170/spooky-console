
from collections import deque, namedtuple
import typing
from networktables.instance import NetworkTablesInstance
from spookyconsole.nt import ntutils


Listener = namedtuple("Listener", ("callback", "flags", "peek_only"))


class NTStream:

    # TODO: send data in specific chunk sizes?

    def __init__(self, kind, receiving_entry=None, transmitting_entry=None, cache_size=100):
        if not (receiving_entry or transmitting_entry):
            raise ValueError("at least one entry must be given")
        self.r_set_func = None
        self.t_set_func = None
        self.receiving_entry = receiving_entry
        self.transmitting_entry = transmitting_entry
        self._listener_callback_id = None
        self._listener_flags = 0
        self._listeners = []
        if receiving_entry:
            self.r_set_func = self._check_entry_type(receiving_entry, kind)
        if transmitting_entry:
            self.t_set_func = self._check_entry_type(transmitting_entry, kind)
            self.cache = deque(maxlen=cache_size)

    def read(self):
        self._assert_readable("cannot read a write-only stream")
        ret = []
        if self._data_available():
            ret = self.receiving_entry.value
            self.r_set_func([])
        return ret

    def write(self, data):
        self._assert_writeable("cannot write to a read-only stream")
        if not isinstance(data, typing.Container) or isinstance(data, str):
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
        self._assert_writeable("cannot write to a read-only stream")
        if not self._output_blocked():
            self.t_set_func(list(self.cache))
            self.cache.clear()

    def peek(self):
        self._assert_readable("cannot read a write-only stream")
        return self.receiving_entry.value

    def new_data_listener(self, func, flags=NetworkTablesInstance.NotifyFlags.UPDATE, peek_only=False):
        self._assert_readable("cannot add a listener to a write-only stream")
        self._check_listening_with_flags(flags)
        self._listeners.append(Listener(func, flags, peek_only))

    def remove_listener(self, func):
        for listener in self._listeners:
            if listener.callback is func:
                break
        else:
            raise ValueError("listener not found")
        self._listeners.remove(listener)
        if not self._listeners:
            self.receiving_entry.removeListener(self._listener_callback_id)
            self._listener_callback_id = None
            self._listener_flags = 0

    def _check_listening_with_flags(self, flags):
        merged = flags | self._listener_flags
        if merged != self._listener_flags:
            if self._listener_callback_id:
                self.receiving_entry.removeListener(self._listener_callback_id)
            self._listener_callback_id = self.receiving_entry.addListener(self._listener_callback, merged, False)
            self._listener_flags = merged

    def _listener_callback(self, entry, key, value, flags):
        clear_after = False
        for listener in self._listeners:
            if (listener.flags & flags) == flags:
                if not listener.peek_only:
                    clear_after = True
                listener.callback(entry, key, value, flags)
        if clear_after:
            self.r_set_func([])

    def _assert_readable(self, msg):
        if not self.readable():
            raise ValueError(msg)

    def _assert_writeable(self, msg):
        if not self.writeable():
            raise ValueError(msg)

    @staticmethod
    def _check_entry_type(entry, kind):
        entry_kind = entry.getType() if entry.exists() else None
        if kind in (NetworkTablesInstance.EntryTypes.BOOLEAN, NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY):
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setBooleanArray([])
            return entry.setBooleanArray
        elif kind in (NetworkTablesInstance.EntryTypes.DOUBLE, NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY):
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setDoubleArray([])
            return entry.setDoubleArray
        else:  # kind in (NetworkTablesInstance.EntryTypes.STRING, NetworkTablesInstance.EntryTypes.STRING_ARRAY)
            if entry_kind and entry_kind != NetworkTablesInstance.EntryTypes.STRING_ARRAY:
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setStringArray([])
            return entry.setStringArray

    @staticmethod
    def _entry_type_error(entry_kind, kind):
        entry_kind = ntutils.type_constant_to_str(entry_kind)
        kind = ntutils.type_constant_to_str(kind)
        raise TypeError("entry type ({}) and given data type ({}) conflict".format(entry_kind, kind))
