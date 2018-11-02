
"""
TODO
"""

from collections import deque, namedtuple
import typing
from networktables.instance import NetworkTablesInstance
from ntcore.constants import NT_UNASSIGNED
from spookyconsole.nt import ntutils


Listener = namedtuple("Listener", ("callback", "flags", "peek_only"))


class NTStream:
    """
    TODO
    """

    def __init__(self, kind, receiving_entry=None, transmitting_entry=None,
                 cache_size=100, min_send_size=0):
        if receiving_entry is None or transmitting_entry is None:
            raise ValueError("at least one entry must be given")
        if cache_size < min_send_size:
            raise ValueError("cache_size must be bigger than min_send_size")
        self.min_send_size = min_send_size
        self.receiving_entry = receiving_entry
        self.transmitting_entry = transmitting_entry
        self._r_set_func = None
        self._t_set_func = None
        self._listener_callback_id = None
        self._listener_flags = 0
        self._listeners = []
        if receiving_entry is not None:
            self._r_set_func = self._check_entry_type(receiving_entry, kind)
        if transmitting_entry is not None:
            self._t_set_func = self._check_entry_type(transmitting_entry, kind)
            self.cache = deque(maxlen=cache_size)
            self.transmitting_entry.addListener(lambda *_: self.flush(False), NetworkTablesInstance.NotifyFlags.UPDATE)

    def read(self):
        self._assert_readable("cannot read a write-only stream")
        ret = []
        if self._data_available():
            ret = self.receiving_entry.value
            self._r_set_func([])
        return ret

    def write(self, data):
        self._assert_writeable("cannot write to a read-only stream")
        if not isinstance(data, typing.Container) or isinstance(data, str):
            data = [data]
        self.cache.extend(data)
        return self.flush(False)

    def readable(self):
        return self._r_set_func is not None

    def writeable(self):
        return self._t_set_func is not None

    def _data_available(self):
        return bool(self.receiving_entry.value)

    def _output_blocked(self):
        return bool(self.transmitting_entry.value)

    def _enough_data_in_cache(self):
        return len(self.cache) >= self.min_send_size

    def flush(self, force=True):
        self._assert_writeable("cannot flush a read-only stream")
        if not self._output_blocked() and (force or self._enough_data_in_cache()):
            # The networktables array setters make an immutable copy of the passed in data, so we're safe to clear the
            # deque after.
            self._t_set_func(self.cache)
            self.cache.clear()
            return True
        return False

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
        merged_flags = flags | self._listener_flags
        if merged_flags != self._listener_flags:
            if self._listener_callback_id:
                self.receiving_entry.removeListener(self._listener_callback_id)
            self._listener_callback_id = self.receiving_entry.addListener(self._listener_callback, merged_flags, False)
            self._listener_flags = merged_flags

    def _listener_callback(self, entry, key, value, flags):
        clear_after = False
        for listener in self._listeners:
            if (listener.flags & flags) == flags:
                if not listener.peek_only:
                    clear_after = True
                listener.callback(entry, key, value, flags)
        if clear_after:
            self._r_set_func([])

    def _assert_readable(self, msg):
        if not self.readable():
            raise ValueError(msg)

    def _assert_writeable(self, msg):
        if not self.writeable():
            raise ValueError(msg)

    @staticmethod
    def _check_entry_type(entry, kind):
        entry_kind = entry.getType()
        if kind in (NetworkTablesInstance.EntryTypes.BOOLEAN, NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY):
            if entry_kind not in (NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY, NT_UNASSIGNED):
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setBooleanArray([])
            return entry.setBooleanArray
        elif kind in (NetworkTablesInstance.EntryTypes.DOUBLE, NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY):
            if entry_kind not in (NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY, NT_UNASSIGNED):
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setDoubleArray([])
            return entry.setDoubleArray
        else:  # kind in (NetworkTablesInstance.EntryTypes.STRING, NetworkTablesInstance.EntryTypes.STRING_ARRAY)
            if entry_kind not in (NetworkTablesInstance.EntryTypes.STRING_ARRAY, NT_UNASSIGNED):
                NTStream._entry_type_error(entry_kind, kind)
            else:
                entry.setStringArray([])
            return entry.setStringArray

    @staticmethod
    def _entry_type_error(entry_kind, kind):
        entry_kind = ntutils.type_constant_to_str(entry_kind)
        kind = ntutils.type_constant_to_str(kind)
        raise TypeError("entry type ({}) and given data type ({}) conflict".format(entry_kind, kind))
