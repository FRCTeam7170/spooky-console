
"""
Contains the ``NTSerializer`` class for serializing data using MessagePack from a
``networktables.entry.NetworkTableEntry`` or a ``spookyconsole.nt.stream.NTStream``.
"""

import os
import typing
import datetime
import msgpack
from networktables.instance import NetworkTablesInstance
from spookyconsole import DATA_PATH


class NTSerializer:
    """
    Class to serialize data to a given file, typically from a ``networktables.entry.NetworkTableEntry`` or
    ``spookyconsole.nt.stream.NTStream``, using MessagePack. New data is added to a cache and serialized and written to
    disk if and only if the length of the cache is of a given minimum size (for performance concerns).

    ``NTSerializer.new_data`` can be used to manually add data to be serialized or the two factory class methods
    ``NTSerializer.from_entry`` and ``NTSerializer.from_stream`` can be used to automatically bind listeners to the
    given entry/stream and serialize data as it comes available.
    """

    DATETIME_PREFIX_FMT = "%d-%m-%Y-%H-%M_"
    """
    The datetime strftime format for filename datetime prefixes.
    Defaults to "<DATE>-<MONTH NUMBER>-<YEAR>-<HOUR>-<MINUTE>_" with zero-padding where appropriate.
    """

    PATH_SEP_REPLACEMENT = "_"
    """
    The string to replace instances of ``networktables.instance.NetworkTablesInstance.PATH_SEPARATOR`` with in entry
    names. This is necessary because the default Network Tables path separator, being a slash ("/"), might conflict with
    the operating system's path separator.
    """

    FILE_EXT = ".msgpack"
    """The filename extension to use."""

    def __init__(self, out_filename, out_dir=DATA_PATH, cache_size=100, datetime_prefix=True):
        """
        :param out_filename: The filename to save the serialized data to, with or without the extension already
        appended.
        :type out_filename: str
        :param out_dir: The directory to place the MessagePack-serialized file in.
        :type out_dir: str
        :param cache_size: The minimum number of data points to cache before serializing them and writing them to disk.
        :type cache_size: int
        :param datetime_prefix: Whether or not to prefix the ``out_filename`` with the datetime data.
        :type datetime_prefix: bool
        """
        if datetime_prefix:
            out_filename = datetime.datetime.now().strftime(self.DATETIME_PREFIX_FMT) + out_filename
        if not out_filename.endswith(self.FILE_EXT):
            out_filename += self.FILE_EXT

        self._path = os.path.join(out_dir, out_filename)
        """The path to the file."""

        self._cache = []
        """A cache (as a list) of data points waiting to be serialized and writen to disk."""

        self._cache_size = cache_size
        """The minimum number of data points to cache before serializing them and writing them to disk."""

        self._already_written = False
        """Whether or not at least one """

    def new_data(self, data):
        """
        Add new data to be serialized.

        :param data: The data to be serialized. May be a single value or some container of multiple values.
        """
        if not isinstance(data, typing.Container) or isinstance(data, str):
            data = [data]
        self._cache.extend(data)
        if len(self._cache) >= self._cache_size:
            self._flush()

    def _flush(self):
        """Flush the cache (i.e. serialize the data in the cache and write it to disk.)"""
        # TODO: This could get really slow... need a better method
        read = []
        # In the event that the given file already exists, checking if we've already written allows us to overwrite any
        # data in that already existing file. Otherwise we might accidentally append to it or cause an error if the data
        # inside cannot be interpreted by MessagePack.
        if self._already_written:
            with open(self._path, "rb") as file:
                read = msgpack.unpack(file)
        else:
            self._already_written = True
        with open(self._path, "wb") as file:
            msgpack.pack(list(read) + self._cache, file)
        self._cache.clear()

    def _on_new_data(self, _, __, value, ___):
        """Used as the callback for entry/stream listeners."""
        self.new_data(value)

    @classmethod
    def from_entry(cls, entry, out_filename=None, **kwargs):
        """
        Create a new ``NTSerializer`` sourced from a ``networktables.entry.NetworkTableEntry``. This adds a listener to
        the given entry to serialize data from the entry as it is updated.

        :param entry: The entry to serialize data from.
        :type entry: networktables.entry.NetworkTableEntry
        :param out_filename: The filename to save the serialized data to. Defaults to the entry's name.
        :type out_filename: str
        :param kwargs: Additional kwargs for the ``NTSerializer`` constructor.
        :return: The ``NTSerializer`` object.
        :rtype: NTSerializer
        """
        out_filename = out_filename or entry.getName()[1:]\
            .replace(NetworkTablesInstance.PATH_SEPARATOR, cls.PATH_SEP_REPLACEMENT)
        ser = cls(out_filename, **kwargs)
        # Listen to changes both remotely (UPDATE flag) and locally (LOCAL flag).
        flags = NetworkTablesInstance.NotifyFlags.UPDATE | NetworkTablesInstance.NotifyFlags.LOCAL
        ser.listener_id = entry.addListener(ser._on_new_data, flags)
        return ser

    @classmethod
    def from_stream(cls, stream, out_filename=None, peek_only=True, **kwargs):
        """
        Create a new ``NTSerializer`` sourced from a ``spookyconsole.nt.stream.NTStream``. This adds a listener to
        the given stream to serialize data from the stream as it is updated. Note that an error will be raise if the
        stream is not readable.

        :param stream: The stream to serialize data from.
        :type stream: spookyconsole.nt.stream.NTStream
        :param out_filename: The filename to save the serialized data to. Defaults to the receiving entry's name.
        :type out_filename: str
        :param peek_only: Whether or not to add the listener in "peek only mode".
        :type peek_only: bool
        :param kwargs: Additional kwargs for the ``NTSerializer`` constructor.
        :return: The ``NTSerializer`` object.
        :rtype: NTSerializer
        """
        if not stream.readable():
            raise ValueError("can only serialize from a readable stream")
        out_filename = out_filename or stream.receiving_entry.getName()[1:]\
            .replace(NetworkTablesInstance.PATH_SEPARATOR, cls.PATH_SEP_REPLACEMENT)
        ser = cls(out_filename, **kwargs)
        # Listen to changes both remotely (UPDATE flag) and locally (LOCAL flag).
        flags = NetworkTablesInstance.NotifyFlags.UPDATE | NetworkTablesInstance.NotifyFlags.LOCAL
        ser.listener_id = stream.new_data_listener(ser._on_new_data, flags, peek_only)
        return ser
