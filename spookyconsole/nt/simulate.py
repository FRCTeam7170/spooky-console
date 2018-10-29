
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

    DEFAULT_TABLE_NAME = "stuff"

    def __init__(self, port=NT_DEFAULT_PORT):
        self._port = port
        self._key_generator = count()
        self._inst = NetworkTablesInstance.create()
        self._inst.startServer(port=port)

    @property
    def _default_table(self):
        return self._inst.getTable(self.DEFAULT_TABLE_NAME)

    def get_receiving_inst(self):
        inst = NetworkTablesInstance.create()
        inst.startClient(("localhost", self._port))
        return inst

    def serve_boolean(self, table=None, key=None, value=None, interval=0):
        return self._serve(table, key, value, interval, "setBoolean", self._rand_bool)

    def serve_double(self, table=None, key=None, value=None, lower=0, upper=10, interval=0):
        return self._serve(table, key, value, interval, "setDouble",
                           partial(self._rand_double, lower, upper))

    def serve_string(self, table=None, key=None, value=None, length=5, interval=0):
        return self._serve(table, key, value, interval, "setString",
                           partial(self._rand_string, length))

    def serve_boolean_array(self, table=None, key=None, value=None, length=10, interval=0):
        return self._serve(table, key, value, interval, "setBooleanArray",
                           partial(self._rand_bool_array, length))

    def serve_double_array(self, table=None, key=None, value=None, length=10, lower=0, upper=10, interval=0):
        return self._serve(table, key, value, interval, "setDoubleArray",
                           partial(self._rand_double_array, length, lower, upper))

    def serve_string_array(self, table=None, key=None, value=None, length=10, str_length=5, interval=0):
        return self._serve(table, key, value, interval, "setStringArray",
                           partial(self._rand_string_array, length, str_length))

    def serve_boolean_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                             length=10, interval=1000):
        return self._serve_stream(table, receive, transmit, cache_size, interval,
                                  partial(self._rand_bool_array, length),
                                  NetworkTablesInstance.EntryTypes.BOOLEAN)

    def serve_double_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, lower=0, upper=10, interval=1000):
        return self._serve_stream(table, receive, transmit, cache_size, interval,
                                  partial(self._rand_double_array, length, lower, upper),
                                  NetworkTablesInstance.EntryTypes.DOUBLE)

    def serve_string_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, str_length=5, interval=1000):
        return self._serve_stream(table, receive, transmit, cache_size, interval,
                                  partial(self._rand_string_array, length, str_length),
                                  NetworkTablesInstance.EntryTypes.STRING)

    def _serve(self, table, key, value, interval, set_func_name, data_func):
        entry = self._table(table).getEntry(self._key(key))
        set_func = getattr(entry, set_func_name)
        if interval:
            self._updater(interval, set_func, data_func)
        else:
            set_func(value or data_func())
        return entry

    def _serve_stream(self, table, receive, transmit, cache_size, interval, data_func, kind):
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
        if transmit:
            self._updater(interval, stream.write, data_func)
        return stream

    def _get_next_key(self):
        return str(next(self._key_generator))

    def _table(self, table):
        if isinstance(table, NetworkTable):
            return table
        elif isinstance(table, str):
            return self._inst.getTable(table)
        return self._default_table

    def _key(self, key):
        return key or self._get_next_key()

    @staticmethod
    def _updater(interval, set_func, data_func):
        def f():
            set_func(data_func())
            time.sleep(interval/1000)
        threading.Thread(target=f).start()

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
    sim.serve_boolean()
    sim.serve_double()
    sim.serve_string()
    input("Press any return to kill simulation...")
