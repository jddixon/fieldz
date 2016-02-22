<h1 class="libTop">Goals</h1>

2012-08-17

Think about performance of fieldz when handling large files: we want to put
U leaf nodes on the wire without repeated copying and certainly without any
sort of bit-shifting.  Typically large files will be read block by block
into a fixed-length buffer (presumably N*4096) and then put on the wire as
soon as available - block by block.  Reading from the wire will follow
a similar pattern.  In either case, whether writing or reading large files,
a data packet will typically have a packed, variegated header followed by a
long 'lenPlus', a varint len followed by that many raw bytes.

Obvious possibility: replace the data from the file with a content key.
The notion might be that there is always at least one U associated with
every connection.  U transfers on the wire look like

	PUT         + key + len + byte[len]
	PUTI + dest + key + len + byte[len]

where PUT means 'write to the machine at the far end of the
connection' and PUTI means write to node 'dest' through the
machine at the far end of the connection.

key and dest may be 160 or 256 bit values (SHA1 or SHA3 digests) or they
may be much shorter varints, indexes into caches shared by the nodes at
the ends of the connection.  The receiver knows from the length of the
encoding (of key or dest) whether it represents the actual value or an
index into a cache of such values.

Note the possible complementary

	GET         + key
	GETI + src  + key

Here 'key' is resolved at the far end; if we knew its length and value,
it would be in our cache and we would not be asking for it.  Similarly
where the operation is PUT or PUTI 'key' must represent a datum in U,
so the sender necessarily knows len and the value, what's in the byte array.

Why are these considerations at the fieldz level?  For the same reason
that varints are.  A varint is (usually) an economical way to represent
a value on the wire.  The fieldz package uses a set of rules to convert
between the varint encoding and raw uint values.  The proposal is to add
content keys to the set of encoding tools available at the fieldz level.

In the PUTI example above, 'dest' is either a varint or a nodeID.  If
it is a varint, the receiver either has it in its cache or it doesn't.
If it doesn't, the receiver can ask for its binding, what it represents.
Otherwise the value it binds to is a key, the nodeID of the destination.
In the proposed scheme, this can be used to fetch the destination's
public key from a local U.  That is

	varint -> cache index -> nodeID -> public key

Each of these refers to the same thing, to the destination node (and as
you go from left to right, each is larger).

Hmmmm.  I think that two different ideas are being commingled here.
First, fieldz needs to be able to put large data files on the wire
and get them back off the wire efficiently.  Data in such files must
not be copied unless absolutely necessary.  It certainly must not be
bit-shifted.  Its integrity must be assured, and the use of longer
content keys (160- or 256-bit digests) is ideal for this.

At another level we can use caches and content keys to actually avoid
transmitting data and to shorten what data is being transmitted.

We also need a layer just above fieldz which converts primitives
(varints, 32- and 64-bit fixed-length values, variable-length
strings) to a richer collection of types.  It might make sense to
put content keys at this level.

Zig-zag encoding is naturally treated in just this way.  We decide
that certain fields in a message are going to come from a range of
small positive and negative values.  So we zig-zag encode the value,
mapping it into a larger range of non-negative values, and then
encode it as a varint.  There is no reason for the fieldz-level logic
to know about the zig-zag encoding.

Encryption is tangled up with all of this.  If we transmit data over
the global Internet, then generally we are going to use fieldz to
prepare data for transmission and then encrypt the result before
transmitting it as one large opaque block.

We also want to be able to use the fieldz code to serialize data
being written to disk.  For example XLattice in its current implementation
stores configuration for a node in XML and then deserializes it at boot
time.  What seems sensible is to replace xlattice.corexml with
xlattice.fieldz and use that for serialization and deserialization.
That is an ambitious objective.
