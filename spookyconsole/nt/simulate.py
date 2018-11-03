
"""Contains the ``NTSimulation`` class for launching Network Tables servers for testing purposes."""

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


class NTSimulation:
    """
    Class to create a Network Tables server for testing purposes.

    If this class is used in the same python interpreter instance as the client code, then one can use
    ``NTSimulation.get_receiving_inst`` to receive a new ``networktables.instance.NetworkTablesInstance`` set up as a
    client.

    Entries of all three basic data types recognized by Network Tables (booleans, doubles, and strings) can easily be
    hosted from the server in the scalar, array, or stream variants using the nine ``serve_...`` methods. In these
    ``serve_...`` methods, the table, entry key, and value are all customizable. In the event that no table is given,
    the default one is used (``NTSimulation.DEFAULT_TABLE_NAME``). In the event that no entry key is given, one is
    generated from an ``itertools.count`` iterator. In the event that no value is given, data is randomly generated
    based on a few other given parameters which vary by entry type. The ``serve_...`` methods also have the option to
    periodically update the entry with a given interval parameter and/or print to stdout whenever a change is remotely
    made to the entry via the ``listen`` parameter. The three stream entry types can even be set up in a "responsive"
    mode where any changes made to the receiving component of a stream will be printed out and then a randomly generated
    response will be returned over the transmitting component of the stream.
    """
    # TODO: option to listen for new keys?

    DEFAULT_TABLE_NAME = "/stuff"
    """
    The table name to use for the ``NTSimulation._default_table``. This should be prefixed with
    ``networktables.instance.NetworkTablesInstance.PATH_SEPARATOR``.
    """

    def __init__(self, port=NT_DEFAULT_PORT):
        """
        :param port: The port to host the server on.
        :type port: int
        """
        self._key_generator = count()
        """Used to generate random keys whenever the user does not explicitly give a key."""

        self._port = port
        self.inst = NetworkTablesInstance.create()
        self.inst.startServer(port=port)

    @property
    def _default_table(self):
        """
        :return: The default table used whenever the user does not explicitly give a table.
        :rtype: networktables.networktable.NetworkTable
        """
        return self.inst.getTable(self.DEFAULT_TABLE_NAME)

    def get_receiving_inst(self):
        """
        Create and return a new Network Tables instance (initialized as a client) connected to this server.

        :return: The created Network Tables instance.
        :rtype: networktables.instance.NetworkTablesInstance
        """
        inst = NetworkTablesInstance.create()
        inst.startClient(("localhost", self._port))
        return inst

    def serve_boolean(self, table=None, key=None, value=None,
                      interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: bool
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setBoolean",
                           self._rand_bool)

    def serve_double(self, table=None, key=None, value=None,
                     lower=0, upper=10, interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: float
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :param lower: The lower bound for randomly generated doubles.
        :type lower: float
        :param upper: The upper bound for randomly generated doubles.
        :type upper: float
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setDouble",
                           partial(self._rand_double, lower, upper))

    def serve_string(self, table=None, key=None, value=None,
                     length=5, interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: str
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :param length: The length for randomly generated strings.
        :type length: int
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setString",
                           partial(self._rand_string, length))

    def serve_boolean_array(self, table=None, key=None, value=None,
                            length=10, interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: bool
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :param length: The length for randomly generated arrays.
        :type length: int
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setBooleanArray",
                           partial(self._rand_bool_array, length))

    def serve_double_array(self, table=None, key=None, value=None,
                           length=10, lower=0, upper=10, interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: float
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :param lower: The lower bound for randomly generated doubles.
        :type lower: float
        :param upper: The upper bound for randomly generated doubles.
        :type upper: float
        :param length: The length for randomly generated arrays.
        :type length: int
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setDoubleArray",
                           partial(self._rand_double_array, length, lower, upper))

    def serve_string_array(self, table=None, key=None, value=None,
                           length=10, str_length=5, interval=0, listen=False):
        """
        :param table: The table to put the entry in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key for the entry, or None to generate a unique one.
        :type key: str
        :param value: An initial value for the entry, or None to randomly generate one.
        :type value: str
        :param interval: How frequently to update the entry, or zero to not update it at all.
        :type interval: int
        :param listen: Whether or not to listen for changes to the entry and print them to stdout.
        :type listen: bool
        :param length: The length for randomly generated arrays.
        :type length: int
        :param str_length: The length for randomly generated strings.
        :type str_length: int
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        return self._serve(table, key, value, interval, listen, "setStringArray",
                           partial(self._rand_string_array, length, str_length))

    def serve_boolean_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                             length=10, transmit_type=0, listen=False):
        """
        :param table: The table to put the stream in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param receive: Whether or not to make the stream readable (as a bool) or a string specifying the name for the
        stream's receiving entry.
        :type receive: str | bool
        :param transmit: Whether or not to make the stream writeable (as a bool) or a string specifying the name for the
        stream's transmitting entry.
        :type transmit: str | bool
        :param cache_size: The size for the stream's cache. This is ignored if ``transmit`` isn't given.
        :type cache_size: int
        :param transmit_type: How frequently to transmit new randomly generated data, or zero to not periodically
        transmit at all, or -1 to put the stream in "responsive mode". This is ignored if ``transmit`` isn't given.
        :type transmit_type: int
        :param listen: Whether or not to listen for changes to the receiving entry and print them to stdout. This is
        ignored if ``receive`` isn't given.
        :type listen: bool
        :param length: The length for randomly generated arrays.
        :type length: int
        :return: The created stream.
        :rtype: spookyconsole.nt.stream.NTStream
        """
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_bool_array, length),
                                  NetworkTablesInstance.EntryTypes.BOOLEAN)

    def serve_double_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, lower=0, upper=10, transmit_type=0, listen=False):
        """
        :param table: The table to put the stream in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param receive: Whether or not to make the stream readable (as a bool) or a string specifying the name for the
        stream's receiving entry.
        :type receive: str | bool
        :param transmit: Whether or not to make the stream writeable (as a bool) or a string specifying the name for the
        stream's transmitting entry.
        :type transmit: str | bool
        :param cache_size: The size for the stream's cache. This is ignored if ``transmit`` isn't given.
        :type cache_size: int
        :param transmit_type: How frequently to transmit new randomly generated data, or zero to not periodically
        transmit at all, or -1 to put the stream in "responsive mode". This is ignored if ``transmit`` isn't given.
        :type transmit_type: int
        :param listen: Whether or not to listen for changes to the receiving entry and print them to stdout. This is
        ignored if ``receive`` isn't given.
        :type listen: bool
        :param lower: The lower bound for randomly generated doubles.
        :type lower: float
        :param upper: The upper bound for randomly generated doubles.
        :type upper: float
        :param length: The length for randomly generated arrays.
        :type length: int
        :return: The created stream.
        :rtype: spookyconsole.nt.stream.NTStream
        """
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_double_array, length, lower, upper),
                                  NetworkTablesInstance.EntryTypes.DOUBLE)

    def serve_string_stream(self, table=None, receive=True, transmit=True, cache_size=100,
                            length=10, str_length=5, transmit_type=0, listen=False):
        """
        :param table: The table to put the stream in as a string or a ``networktables.networktable.NetworkTable``.
        Passing in None means to use the default table.
        :type table: str | networktables.networktable.NetworkTable
        :param receive: Whether or not to make the stream readable (as a bool) or a string specifying the name for the
        stream's receiving entry.
        :type receive: str | bool
        :param transmit: Whether or not to make the stream writeable (as a bool) or a string specifying the name for the
        stream's transmitting entry.
        :type transmit: str | bool
        :param cache_size: The size for the stream's cache. This is ignored if ``transmit`` isn't given.
        :type cache_size: int
        :param transmit_type: How frequently to transmit new randomly generated data, or zero to not periodically
        transmit at all, or -1 to put the stream in "responsive mode". This is ignored if ``transmit`` isn't given.
        :type transmit_type: int
        :param listen: Whether or not to listen for changes to the receiving entry and print them to stdout. This is
        ignored if ``receive`` isn't given.
        :type listen: bool
        :param length: The length for randomly generated arrays.
        :type length: int
        :param str_length: The length for randomly generated strings.
        :type str_length: int
        :return: The created stream.
        :rtype: spookyconsole.nt.stream.NTStream
        """
        return self._serve_stream(table, receive, transmit, cache_size, transmit_type, listen,
                                  partial(self._rand_string_array, length, str_length),
                                  NetworkTablesInstance.EntryTypes.STRING)

    def _serve(self, table, key, value, interval, listen, set_func_name, data_func):
        """
        Internal method to serve any of the six basic (non-stream) entry types.

        :param set_func_name: The name of the entry's set method.
        :type set_func_name: str
        :param data_func: Callable that generates random data for the entry.
        :return: The created entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        entry = self._get_entry(table, key)
        set_func = getattr(entry, set_func_name)
        if interval:
            # Set up a thread to update the entry periodically if we're given an interval.
            self._updater(interval, set_func, data_func)
        else:
            # Otherwise, give the entry an initial value.
            set_func(value or data_func())
        if listen:
            # Set up a listener callback print to stdout whenever the entry is updated.
            entry.addListener(self._listen_callback, NetworkTablesInstance.NotifyFlags.UPDATE)
        return entry

    def _serve_stream(self, table, receive, transmit, cache_size, transmit_type, listen, data_func, kind):
        """
        Internal method to serve any of the three stream types.

        :param data_func: Callable that generates random data for the stream. Ignored if ``transmit`` isn't given.
        :param kind: One of the six ``networktables.instance.NetworkTablesInstance.EntryTypes``.
        :return: The created stream.
        :rtype: spookyconsole.nt.stream.NTStream
        """
        # Assert that at least one of receive or transmit is given.
        if not (receive or transmit):
            raise ValueError("at least one of 'receive' or 'transmit' must be given")
        receive_entry, transmit_entry = None, None
        if receive:
            key = receive if isinstance(receive, str) else None
            receive_entry = self._get_entry(table, key)
        if transmit:
            key = transmit if isinstance(transmit, str) else None
            transmit_entry = self._get_entry(table, key)
        stream = ntstream.NTStream(kind, receive_entry, transmit_entry, cache_size)
        if receive:
            if transmit and transmit_type == -1:
                # Set up a listener for responsive mode.
                stream.new_data_listener(partial(self._stream_responder_callback, stream, data_func))
            elif listen:
                # Set up a regular listener.
                stream.new_data_listener(self._listen_callback)
        if transmit and transmit_type > 0:
            # Set up an updater in another thread. Note this will never happen if the stream is in responsive mode.
            self._updater(transmit_type, stream.write, data_func)
        return stream

    def _get_next_key(self):
        """
        :return: The next key from the ``NTSimulate._key_generator`` as a string.
        :rtype: str
        """
        return str(next(self._key_generator))

    def _get_entry(self, table, key):
        """
        Return the entry specified by ``table`` and ``key``. If table isn't given, the default one is used. If key isn't
        given, a unique key is generated.

        :param table: The table name, the table itself, or None.
        :type table: str | networktables.networktable.NetworkTable
        :param key: The key name or None.
        :type key: str
        :return: The entry.
        :rtype: networktables.entry.NetworkTableEntry
        """
        # Set the table if one is not directly given.
        if isinstance(table, str):
            table = self.inst.getTable(table)
        elif not isinstance(table, NetworkTable):
            table = self._default_table

        # Generate a unique key if one isn't given
        if not key:
            key = self._get_next_key()
            while table.containsKey(key):
                key = self._get_next_key()

        return table.getEntry(key)

    @staticmethod
    def _listen_callback(_, key, value, __):
        """
        Function used as the callback for listening entries. This simply prints the change made to the entry to stdout.
        """
        print("{!r} updated: {!r}".format(key, value))

    @staticmethod
    def _stream_responder_callback(stream, data_func, _, key, value, __):
        """
        Function used as the callback for responsive streams. This sets the transmitting entry with random data and
        prints the change made to the receiving entry and the change to be made to the transmitting entry to stdout.

        :param stream: The stream being updated.
        :type stream: spookyconsole.nt.stream.NTStream
        :param data_func: Callable that generates random data for the stream.
        """
        # Generate random data.
        data = data_func()
        print("{!r} updated: {!r}...Responding with {!r}".format(key, value, data))
        stream.write(data)

    @staticmethod
    def _updater(interval, set_func, data_func):
        """
        Create a thread to periodically update an entry with random data.

        :param interval: How long to sleep in between updates in milliseconds.
        :type interval: int
        :param set_func: The entry's set method.
        :param data_func: Callable that generates random data for the entry.
        """
        interval /= 1000

        def f():
            while True:
                set_func(data_func())
                time.sleep(interval)

        threading.Thread(target=f, daemon=True).start()

    @staticmethod
    def _rand_bool():
        """
        Generate a random boolean.

        :return: The randomly generated boolean.
        :rtype: bool
        """
        return bool(random.randint(0, 1))

    @staticmethod
    def _rand_double(lower, upper):
        """
        Generate a random float in [``lower``, ``upper``].

        :param lower: The lower bound for the float.
        :type lower: float
        :param upper: The upper bound for the float.
        :type upper: float
        :return: The randomly generated float.
        :rtype: float
        """
        return random.random() * (upper - lower) + lower

    @staticmethod
    def _rand_string(length):
        """
        Generate a random string of the given length composed of ASCII letters (lowercase or uppercase).

        :param length: The length of the string.
        :type length: int
        :return: The randomly generated string.
        :rtype: str
        """
        ret = ""
        for i in range(length):
            ret += random.choice(string.ascii_letters)
        return ret

    @staticmethod
    def _rand_bool_array(length):
        """
        Generate a list of the given length containing random booleans.

        :param length: The length of the list.
        :type length: int
        :return: The randomly generated list of booleans.
        :rtype: list
        """
        return [NTSimulation._rand_bool() for _ in range(length)]

    @staticmethod
    def _rand_double_array(length, lower, upper):
        """
        Generate a list of the given length containing random floats in [``lower``, ``upper``].

        :param length: The length of the list.
        :type length: int
        :param lower: The lower bound for the floats.
        :type lower: float
        :param upper: The upper bound for the floats.
        :type upper: float
        :return: The randomly generated list of floats.
        :rtype: list
        """
        return [NTSimulation._rand_double(lower, upper) for _ in range(length)]

    @staticmethod
    def _rand_string_array(length, str_length):
        """
        Generate a list of the given length containing random strings of the given size composed of ASCII letters
        (lowercase or uppercase).

        :param length: The length of the list.
        :type length: int
        :param length: The length of the strings.
        :type length: int
        :return: The randomly generated list of strings.
        :rtype: list
        """
        return [NTSimulation._rand_string(str_length) for _ in range(length)]


if __name__ == '__main__':
    sim = NTSimulation()
    sim.serve_boolean(listen=True)
    sim.serve_double(listen=True)
    sim.serve_string(listen=True)
    sim.serve_double_array("/stuff/othertable", listen=True)
    sim.serve_string_stream("/stuff/othertable", transmit_type=-1)
    input("Press return to kill simulation...\n")
