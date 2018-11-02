
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
the datum was received and the next piece of datum can be sent; for a data source producing data rapidly, this solution
would be far too slow. We thus turn to the array data types, which allow one to efficiently send data in blocks. The
array solution, however, requires regulation: the spooky-console Network Tables Stream Protocol.


Basic Overview
--------------

The spooky-console Network Tables Stream Protocol is very simple. It works by having the receiving side of a stream
(hereby to be referred to as the "receiver") use an empty array response as an indicator that the sending side of a
stream (hereby to be referred to as the "sender") may send the next array of data. In this way, only one Network Tables
entry is required for unidirectional stream communication; bidirectional communication can be achieved with two entries,
one for receiving and one for transmitting. Note that this protocol only supports communication between two parties.

There is no default way for a participant in a Network Tables network to identify which entries are streams and which
are not (i.e. no "handshake" procedure, etc.); this is expected to be known by all participants in advance.


Receiving
---------

The receiver has three basic principles to uphold:

 - To accept any received data from the sender as quickly as possible to permit the transfer of new data. This is
   critical if the sender employs a cache system because the sender will be forced, due to memory concerns, to
   eventually start deleting old cached data.

 - To set the Network Tables entry to an empty array after each block of data has been received.

 - To never set the Network Tables entry to anything other than an empty array.


Transmitting
------------

The sender, being in control of how quickly data is sent, only has one important principle to uphold: to never set the
entry while there is still data in it.

Although it is not required, the sender should only send data in blocks of a specific minimum size. The exact minimum
block size will vary, but, in general, should be proportional to the rate of data generated. Following this
recommendation will help reduce the overhead delays inherent to networking and a potentially delayed response from the
receiver.

The sender will likely be required to employ a cache system to save any data generated while waiting for a response from
the receiver. If the minimum send size recommendation is followed, such a cache system would also prove helpful in that
data can be added to the cache until a minimum cache size is reached, at which point the entry can be set and the cache
can be cleared.
