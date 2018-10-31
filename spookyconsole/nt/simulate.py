
import random
import string
from itertools import count
from functools import partial
import threading
import time
from networktables.instance import NetworkTablesInstance
from networktables.networktable import NetworkTable
from ntcore.constants import NT_DEFAULT_PORT
from spookyconsole.nt import stream as ntstream


class Simulation:

    DEFAULT_TABLE_NAME = "/stuff"

    def __init__(self, port=NT_DEFAULT_PORT):
        self._port = port
        self._key_generator = count()
        self.inst = NetworkTablesInstance.create()
        self.inst.startServer(port=port)

    @property
    def _default_table(self):
        return self.inst.getTable(self.DEFAULT_TABLE_NAME)

    def get_receiving_inst(self):
        inst = NetworkTablesInstance.create()
        inst.startClient(("localhost", self._port))
        return inst

    def serve_boolean(self, table=None, key=None, value=None,
                      interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setBoolean",
                           self._rand_bool)

    def serve_double(self, table=None, key=None, value=None,
                     lower=0, upper=10, interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setDouble",
                           partial(self._rand_double, lower, upper))

    def serve_string(self, table=None, key=None, value=None,
                     length=5, interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setString",
                           partial(self._rand_string, length))

    def serve_boolean_array(self, table=None, key=None, value=None,
                            length=10, interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setBooleanArray",
                           partial(self._rand_bool_array, length))

    def serve_double_array(self, table=None, key=None, value=None,
                           length=10, lower=0, upper=10, interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setDoubleArray",
                           partial(self._rand_double_array, length, lower, upper))

    def serve_string_array(self, table=None, key=None, value=None,
                           length=10, str_length=5, interval=0, listen=False):
        return self._serve(table, key, value, interval, listen, "setStringArray",
                           partial(self._rand_string_array, length, str_length))

    def serve_boolean_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                             length=10, transmit_type=0, listen=False):
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_bool_array, length),
                                  NetworkTablesInstance.EntryTypes.BOOLEAN)

    def serve_double_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, lower=0, upper=10, transmit_type=0, listen=False):
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_double_array, length, lower, upper),
                                  NetworkTablesInstance.EntryTypes.DOUBLE)

    def serve_string_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, str_length=5, transmit_type=0, listen=False):
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_string_array, length, str_length),
                                  NetworkTablesInstance.EntryTypes.STRING)

    def _serve(self, table, key, value, interval, listen, set_func_name, data_func):
        entry = self._table(table).getEntry(self._key(key))
        set_func = getattr(entry, set_func_name)
        if interval:
            self._updater(interval, set_func, data_func)
        else:
            set_func(value or data_func())
        if listen:
            return entry, entry.addListener(self._listen_callback, NetworkTablesInstance.NotifyFlags.UPDATE)
        return entry, None

    def _serve_stream(self, table, receive, transmit, cache_size, transmit_type, listen, data_func, kind):
        if not (receive or transmit):
            raise ValueError("at least one of 'receive' or 'transmit' must be given")
        receive_entry, transmit_entry = None, None
        if receive:
            key = receive if isinstance(receive, str) else None
            receive_entry = self._table(table).getEntry(self._key(key))
        if transmit:
            key = transmit if isinstance(transmit, str) else None
            transmit_entry = self._table(table).getEntry(self._key(key))
        stream = ntstream.NTStream(kind, receive_entry, transmit_entry, cache_size)
        if receive:
            if transmit_type == -1:
                stream.new_data_listener(partial(self._stream_responder_callback, stream, data_func))
            elif listen:
                stream.new_data_listener(self._listen_callback)
        if transmit and transmit_type > 0:
            self._updater(transmit_type, stream.write, data_func)
        return stream

    def _get_next_key(self):
        return str(next(self._key_generator))

    def _table(self, table):
        if isinstance(table, NetworkTable):
            return table
        elif isinstance(table, str):
            return self.inst.getTable(table)
        return self._default_table

    def _key(self, key):
        return key or self._get_next_key()

    @staticmethod
    def _listen_callback(_, key, value, __):
        print("{!r} updated: {!r}".format(key, value))

    @staticmethod
    def _stream_responder_callback(stream, data_func, _, key, value, __):
        data = data_func()
        print("{!r} updated: {!r}...Responding with {!r}".format(key, value, data))
        stream.write(data)

    @staticmethod
    def _updater(interval, set_func, data_func):
        def f():
            while True:
                set_func(data_func())
                time.sleep(interval/1000)
        threading.Thread(target=f, daemon=True).start()

    @staticmethod
    def _rand_bool():
        return bool(random.randint(0, 1))

    @staticmethod
    def _rand_double(lower, upper):
        return random.random() * (upper - lower) + lower

    @staticmethod
    def _rand_string(length):
        ret = ""
        for i in range(length):
            ret += random.choice(string.ascii_letters)
        return ret

    @staticmethod
    def _rand_bool_array(length):
        return [Simulation._rand_bool() for _ in range(length)]

    @staticmethod
    def _rand_double_array(length, lower, upper):
        return [Simulation._rand_double(lower, upper) for _ in range(length)]

    @staticmethod
    def _rand_string_array(length, str_length):
        return [Simulation._rand_string(str_length) for _ in range(length)]


if __name__ == '__main__':
    sim = Simulation()
    sim.serve_boolean(listen=True)
    sim.serve_double(listen=True)
    sim.serve_string(listen=True)
    sim.serve_double_array("/stuff/othertable", listen=True)
    sim.serve_string_stream("/stuff/othertable", transmit_type=-1)
    input("Press return to kill simulation...\n")
