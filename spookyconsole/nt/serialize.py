
import os
import typing
import datetime
import msgpack
from networktables.instance import NetworkTablesInstance
from spookyconsole import DATA_PATH


class NTSerializer:

    DATETIME_PREFIX_FMT = "%d-%m-%Y-%H-%M_"
    PATH_SEP_REPLACEMENT = "_"
    FILE_EXT = ".msgpack"

    def __init__(self, out_filename, out_dir=DATA_PATH, cache_size=100, datetime_prefix=True):
        if datetime_prefix:
            out_filename = datetime.datetime.now().strftime(self.DATETIME_PREFIX_FMT) + out_filename
        if not out_filename.endswith(self.FILE_EXT):
            out_filename += self.FILE_EXT
        self._path = os.path.join(out_dir, out_filename)
        self._cache = []
        self._cache_size = cache_size
        self._already_written = False

    def new_data(self, data):
        if not isinstance(data, typing.Container) or isinstance(data, str):
            data = [data]
        if self._cache:
            self._cache.extend(data)
        else:
            self._cache = data
        if len(self._cache) >= self._cache_size:
            self._flush()

    def _flush(self):
        # TODO: This could get really slow... need a better method
        read = []
        if self._already_written:
            with open(self._path, "rb") as file:
                read = msgpack.unpack(file)
        else:
            self._already_written = True
        with open(self._path, "wb") as file:
            msgpack.pack(list(read) + self._cache, file)
        self._cache = []

    def _on_new_data(self, _, __, value, ___):
        self.new_data(value)

    @classmethod
    def from_entry(cls, entry, out_filename=None, **kwargs):
        out_filename = out_filename or entry.getName()[1:]\
            .replace(NetworkTablesInstance.PATH_SEPARATOR, cls.PATH_SEP_REPLACEMENT)
        ser = cls(out_filename, **kwargs)
        flags = NetworkTablesInstance.NotifyFlags.UPDATE | NetworkTablesInstance.NotifyFlags.LOCAL
        ser.listener_id = entry.addListener(ser._on_new_data, flags)
        return ser

    @classmethod
    def from_stream(cls, stream, out_filename=None, **kwargs):
        out_filename = out_filename or stream.receiving_entry.getName()[1:]\
            .replace(NetworkTablesInstance.PATH_SEPARATOR, cls.PATH_SEP_REPLACEMENT)
        ser = cls(out_filename, **kwargs)
        flags = NetworkTablesInstance.NotifyFlags.UPDATE | NetworkTablesInstance.NotifyFlags.LOCAL
        ser.listener_id = stream.new_data_listener(ser._on_new_data, flags)
        return ser
