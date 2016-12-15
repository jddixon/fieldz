<h1 class="libTop">Channels</h1>

2012-09-16, edited -09-21

Channel communications may be nested.  The lowest level channel represents
a point-to-point link between nodes.  Keep-alives are run at this level.
It might be useful to look at hardware P2P link protocols.  Call this
lowest level a p2p channel.

Tentatively a p2p channel consists of two paired links.  The owner
of a channel can send on one link and receive on the other.  There is a
buffer associated with each link.  These are send and receive buffers.

There must be a buffer associated with each direction, but such
a buffer can be replaced.  Buffers can be initialized (cleared)
at any time.  A buffer has an offset, limit, and capacity.  Initializing
a buffer resets the offset to zero and the limit to the buffer's
capacity.  The limit may be set to any value between the offset and the
capacity, inclusive.

P2P channels are paired.  One channel acts as the client, or initiator.
The other acts as the server, or reactive component.

From either side the offset, limit, and capacity of the channel can
be read.  The channel can also be initialized.  Writing to the
buffer increases the offset accordingly, but not beyond the limit.
The limit can be set at any time.

## Opening a Channel

From the clients's point of view the channel is either open or closed.
Opening the channel sets a timeout to a non-negative number of seconds.
By default the timeout is zero, interpreted as meaning infinity.  If
the timeout occurs, the channel is closed.

When the client opens the channel, an initial keep-alive message is sent
to the server.  This specifies the timeout on the channel.

After opening the channel, the channel can send either a switch protocol
message or any number of keepalives.

## Protocol Negotiation

The switch protocol message is an fbytes20, interpreteted by the server
as the content hash of a protocol.   The server can reply with an OK, after
which data packets are treated as messages in that protocol, or it can
reply with a

	GetProto fbytes20           # the hash

to which the client should reply

	PUT fbytes20 lbytes         # the content hash, length, that many bytes

If this is consistent (the length corresponds to the number of bytes sent
and the the payload hashes to the expected value) the server replies OK
and protocol-based traffic starts.

If the PUT message is inconsistent, the server will reply with an

	ErrorMsg vuint32 lstring    # code, text

and close the connection.

## Protocol-based Communications

At this level, further communications at this level consist of

	client                      server

	KeepAlive                   Ack
	DataMsg lbytes              DataReply lbytes
	SwitchProto fbytes20        OK | GetProto fbytes20
	PutProto fbytes20 lbytes    OK | ErrMsag vuint32 lstring
	ErrMsg vuint32 lstring      .

This is the core protocol plus the DataMsg and DataReply messages
with their opaque content.

If the client sends SwitchProto NoProto, where NoProto is an fbytes20
consisting of 20 zero bytes, there is no active prototocol, and a
DataMsg or DataReply will cause an ErrMsg to be sent by the opposite
and the channel to be closed.

None of this traffic is visible to clients, except that the buffer
holding the DataMsg will have been written by the client and the
buffer holding the DataReply will be switched into the client's
view.

## Higher Level Channels

The client initiates communications by associating a channel with
its application.  This channel uses the lower level channel for
communications.

The client application opens the higher level channel with a

	chan = DataChannel.open(endPoint, protocolName)

command.  This finds the CoreChannel associated with the endpoint
and causes it to be associated with the protocol.  That is, the
client CoreChannel sends a SwitchProto message to the far end; if
this succeeds, the DataChannel is opened, bound to the new protocol.
The client application can then send and receive messages using the
designated protocol.

Higher level protocols will generally import OK, Ack, and ErrMsg from
the core protocol.

## Routing

Routing protocols are very similar to the core protocol in that they
have few message types and that these include GET and PUT operations
on opaque data.


