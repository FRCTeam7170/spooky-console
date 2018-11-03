
from collections import deque, namedtuple
import typing
from networktables.instance import NetworkTablesInstance
from ntcore.constants import NT_UNASSIGNED
from spookyconsole.nt import ntutils


Listener = namedtuple("Listener", ("callback", "flags", "peek_only"))


class NTStream:
    """
    An implementation of the spooky-console stream protocol, supporting uni- or bidirectional communication controlled
    by supplying the appropriate entries (receiving or transmitting) upon construction. If neither entry is given, an
    error will occur.

    This implementation supports a minimum send size and a caching system for transmitting streams.

    Receiving streams can register listeners, optionally in "peek mode", meaning the data will remain in the entry even
    after the callback to the listener takes place (otherwise the entry will be cleared after the callback). Multiple
    listeners can be registered in which case the entry will not be reset until all listener callbacks have occurred.
    """

    def __init__(self, kind, receiving_entry=None, transmitting_entry=None,
                 cache_size=100, min_send_size=0):
        """
        :param kind: One of the ``networktables.instance.NetworkTablesInstance.EntryTypes``. In this case, the array
        versions of the three types are considered synonymous with the scalar ones.
        :param receiving_entry: The entry to use for the receiving data stream, or None to not receive data.
        :type receiving_entry: networktables.entry.NetworkTableEntry
        :param transmitting_entry: The entry to use for the transmitting data stream, or None to not transmit data.
        :type transmitting_entry: networktables.entry.NetworkTableEntry
        :param cache_size: The amount of data to cache in transmitting streams before discarding old data.
        :type cache_size: int
        :param min_send_size: The minimum number of data points to send at once in transmitting streams.
        :type min_send_size: int
        """
        if receiving_entry is None or transmitting_entry is None:
            raise ValueError("at least one entry must be given")
        # If the cache_size is smaller than the min_send_size, we'll never be able to send anything!
        if transmitting_entry and cache_size < min_send_size:
            raise ValueError("cache_size must be bigger than min_send_size")

        self.receiving_entry = receiving_entry
        """The ``networktables.entry.NetworkTableEntry`` used for receiving data."""

        self.transmitting_entry = transmitting_entry
        """The ``networktables.entry.NetworkTableEntry`` used for transmitting data."""

        self.min_send_size = None
        """The amount of data to cache in transmitting streams before discarding old data."""

        self.cache = None
        """The cache for transmitting streams."""

        if receiving_entry is not None:
            self._listener_callback_id = None
            """
            The listener id for receiving streams. This is only non-None when one or more listeners are registered.
            """

            self._listener_flags = 0
            """
            The ``networktables.instance.NetworkTablesInstance.NotifyFlags`` under which this receiving stream is
            currently listening.
            """

            self._listeners = []
            """A list of user-registered listeners as instances of the ``Listener`` namedtuple."""

            self._r_set_func = self._check_entry_type(receiving_entry, kind)
            """The function used to set data on the receiving entry."""

        if transmitting_entry is not None:
            # These are only set when this is a transmitting stream. They default to None, however, because they are
            # public.
            self.min_send_size = min_send_size
            self.cache = deque(maxlen=cache_size)

            self._t_set_func = self._check_entry_type(transmitting_entry, kind)
            """The function used to set data on the transmitting entry."""

            self.transmitting_entry.addListener(lambda *_: self.flush(False), NetworkTablesInstance.NotifyFlags.UPDATE)

    def read(self):
        """
        Read the stream. This will fail if the stream is not readable.

        :return: The read values, or an empty tuple if no data was read.
        :rtype: tuple
        """
        self._assert_readable("cannot read a write-only stream")
        # pynetworktables stores array values as tuples.
        ret = ()
        if self._data_available():
            ret = self.receiving_entry.value
            # Write an empty array to the receiving entry to signal to the sender that more data can be sent.
            self._r_set_func([])
        return ret

    def write(self, data):
        """
        Write the given data to the stream. This will fail if the stream is not writeable.

        :param data: The data to write. May be a single value or some container of multiple values.
        :return: Whether or not the cache was flushed (i.e. data was actually set over the transmitting entry) after
        writing.
        :rtype: bool
        """
        self._assert_writeable("cannot write to a read-only stream")
        # Convert the data into a list if it is a single value.
        if not isinstance(data, typing.Container) or isinstance(data, str):
            data = [data]
        self.cache.extend(data)
        return self.flush(False)

    def readable(self):
        """
        :return: Whether or not this stream can be read.
        :rtype: bool
        """
        return self.receiving_entry is not None

    def writeable(self):
        """
        :return: Whether or not this stream can be written to.
        :rtype: bool
        """
        return self.transmitting_entry is not None

    def _data_available(self):
        """
        :return: Whether or not there's data in the receiving entry waiting to be read.
        :rtype: bool
        """
        return bool(self.receiving_entry.value)

    def _output_blocked(self):
        """
        :return: Whether or not there's data in the transmitting entry blocking write operations.
        :rtype: bool
        """
        return bool(self.transmitting_entry.value)

    def _enough_data_in_cache(self):
        """
        :return: Whether or not there's enough data in the cache to be written.
        :rtype: bool
        """
        return len(self.cache) >= self.min_send_size

    def flush(self, force=True):
        """
        Flush the cache. This will only work if the transmitting entry is empty. This will fail if the stream is not
        writeable.

        :param force: Whether or not to flush the cache regardless of if enough data is in it.
        :type force: bool
        :return: Whether or not the cache was successfully flushed.
        :rtype: bool
        """
        self._assert_writeable("cannot flush a read-only stream")
        if not self._output_blocked() and (force or self._enough_data_in_cache()):
            # The networktables array setters make an immutable copy of the passed in data, so we're safe to clear the
            # cache (deque) after.
            self._t_set_func(self.cache)
            self.cache.clear()
            return True
        return False

    def peek(self):
        """
        Return the value in the receiving entry without clearing the receiving entry. This will fail if the stream is
        not readable.

        :return: The value in the receiving entry.
        :rtype: tuple
        """
        self._assert_readable("cannot read a write-only stream")
        return self.receiving_entry.value

    def new_data_listener(self, func, flags=NetworkTablesInstance.NotifyFlags.UPDATE, peek_only=False):
        """
        Add a listener for new data to the stream. This will fail if the stream is not readable.

        The listener may be registered in "peek mode", meaning the data will remain in the receiving entry even after
        the callback to the listener takes place (otherwise the entry will be cleared after the callback). Multiple
        listeners can be registered in which case the entry will not be reset until all listener callbacks have
        occurred.

        :param func: The listener callback.
        :type func: function
        :param flags: A bitmask of ``networktables.instance.NetworkTablesInstance.NotifyFlags`` flags to listen for.
        :type flags: int
        :param peek_only: Whether or not to register the listener in "peek mode" (see above).
        :type peek_only: bool
        """
        self._assert_readable("cannot add a listener to a write-only stream")
        self._check_listening_with_flags(flags)
        self._listeners.append(Listener(func, flags, peek_only))

    def remove_listener(self, func):
        """
        Remove the listener ``func`` from this stream. This will fail if the stream is not readable or if the listener
        was not previously registered to this stream.

        :param func: The listener to remove.
        :type func: function
        """
        self._assert_readable("cannot remove a listener from a write-only stream")
        # Search for the give listener func in the registered listeners.
        for listener in self._listeners:
            if listener.callback is func:
                break
        else:
            # Error if the listener wasn't found.
            raise ValueError("listener not found")
        self._listeners.remove(listener)
        # If, after removing that listener, no more listeners are registered to this stream, deactivate the listener
        # callback.
        if not self._listeners:
            self.receiving_entry.removeListener(self._listener_callback_id)
            self._listener_callback_id = None
            self._listener_flags = 0

    def _check_listening_with_flags(self, flags):
        """
        Make sure this stream is listening with the given flags. If it's not, remove the old listener (should it exist)
        and register a new one with the updated flags.

        :param flags: The flags with which this stream should be listening
        :type flags: int
        """
        merged_flags = flags | self._listener_flags
        if merged_flags != self._listener_flags:
            # The stream might not even be listening at all yet!
            if self._listener_callback_id:
                self.receiving_entry.removeListener(self._listener_callback_id)
            self._listener_callback_id = self.receiving_entry.addListener(self._listener_callback, merged_flags, False)
            self._listener_flags = merged_flags

    def _listener_callback(self, entry, key, value, flags):
        """
        Internal method used as the listener callback. This method iterates through all the user-defined callbacks and
        invokes each one in the order added if they were registered with the flag(s) that triggered this callback. If
        at least one of the user-defined callbacks is not in "peek mode", clear the receiving entry afterwards.
        """
        clear_after = False
        for listener in self._listeners:
            if (listener.flags & flags) == flags:
                if not listener.peek_only:
                    clear_after = True
                listener.callback(entry, key, value, flags)
        if clear_after:
            self._r_set_func([])

    def _assert_readable(self, msg):
        """
        Assert that this stream is readable.

        :param msg: The error message to use if the assertion fails.
        :type msg: str
        """
        if not self.readable():
            raise ValueError(msg)

    def _assert_writeable(self, msg):
        """
        Assert that this stream is writeable.

        :param msg: The error message to use if the assertion fails.
        :type msg: str
        """
        if not self.writeable():
            raise ValueError(msg)

    @staticmethod
    def _check_entry_type(entry, kind):
        """
        Assert that the given entry is of the given data type ``kind`` and return the appropriate setter method for the
        entry if the assertion passes. If the entry's data type is not yet assigned, force it to be of the appropriate
        array type by assigning an empty array.

        :param entry: The entry whose type to check.
        :type entry: networktables.entry.NetworkTableEntry
        :param kind: One of the ``networktables.instance.NetworkTablesInstance.EntryTypes``. In this case, the array
        versions of the three types are considered synonymous with the scalar ones.
        :return: The appropriate setter method for the entry.
        :rtype: function
        """
        entry_kind = entry.getType()

        def _entry_type_error():
            entry_kind_str = ntutils.type_constant_to_str(entry_kind)
            kind_str = ntutils.type_constant_to_str(kind)
            raise TypeError("entry type ({}) and given data type ({}) conflict".format(entry_kind_str, kind_str))

        # Note that the scalar types and their corresponding array types are considered synonymous.
        if kind in (NetworkTablesInstance.EntryTypes.BOOLEAN, NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY):
            if entry_kind == NT_UNASSIGNED:
                entry.setBooleanArray([])
            elif entry_kind != NetworkTablesInstance.EntryTypes.BOOLEAN_ARRAY:
                _entry_type_error()
            return entry.setBooleanArray
        elif kind in (NetworkTablesInstance.EntryTypes.DOUBLE, NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY):
            if entry_kind == NT_UNASSIGNED:
                entry.setDoubleArray([])
            elif entry_kind != NetworkTablesInstance.EntryTypes.DOUBLE_ARRAY:
                _entry_type_error()
            return entry.setDoubleArray
        else:  # kind in (NetworkTablesInstance.EntryTypes.STRING, NetworkTablesInstance.EntryTypes.STRING_ARRAY)
            if entry_kind == NT_UNASSIGNED:
                entry.setStringArray([])
            elif entry_kind != NetworkTablesInstance.EntryTypes.STRING_ARRAY:
                _entry_type_error()
            return entry.setStringArray
