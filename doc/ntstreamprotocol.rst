
===========================================================
spooky-console Network Tables Stream Protocol Specification
===========================================================


.. contents::
    :depth: 2


Philosophy
----------

The Network Tables protocol recognizes six basic data types: booleans, double-precision floating point numbers, strings,
and array versions of the previous three types. These six types are sufficient for static data or rarely-updated dynamic
data. Suppose, however, one desires to transmit volatile dynamic data across a Network Tables network and retain every
datum point. If this data updates rapidly enough, one quickly comes to eliminate the three scalar types as possibles
means of communication since, as recommended in the
`Network Tables v3 Specification <https://github.com/wpilibsuite/ntcore/blob/master/doc/networktables3.adoc#bandwidth-and-latency-considerations>`_,
a good Network Tables implementation should discard old entry data in favour of new data if the old data has not yet
been broadcast to other nodes on the Network Tables network. If one were to use the three scalar types for this purpose,
one would have to transmit a single piece of datum across the entry and wait for a response from the client indicating
the data was received and the next piece of datum can be sent; for a data source producing data rapidly, this solution
would be far too slow. We thus turn to the array data types, which allow one to efficiently send data in blocks. The
array solution, however, requires regulation: the spooky-console Network Tables Stream Protocol.


Transmitting
------------


Receiving
---------
