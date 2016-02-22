<h1 class="libTop">API</h1>

2012-09-21

I have just finished sketching out a crude data model, one populated
by

* protocols, which are lists of enums and messages plus some sequencing
    rules
* enums, which map simple symbols (strings containing no delimiters,
    no dots, and no slashes) to integer values; in the current
    implementation the values may not be negative
* messages, where a message is a container for locally defined enums and
    nested messages, plus a list of sequencing rules
* fields, which are named and numbered, contain a value, and specify an
    encoding/decoding scheme; there are currently 18 such schemes, one
    allowing methods to be nested.  In addition fields have a quantifier
    which specifies whether the field must contain a single value (the
    default), or may or may not be present ('?'), or may be present
    zero or more times ('*'), or may be present one or more times ('+').

In the current implementation fields must appear in the serialized message
in increasing order.  That is, when serializing the message the field with
the lowest field number is written first and then the field number of each
field written is greater than or equal to that of the preceding field.
It can be assumed that where field quantifiers permit multiple instances
the instances of the same field number are written in the order in which
they were appended to the message.

In today's code, the message class is dynamically generated, subclassing
MsgImpl.  In the simplest case we generate something like LogEntryMsg,
which has 5 required fields: timestamp, nodeID, key, by, and path.  The
first is an unsigned 32-bit integer which should default to int(time.time()).
The second and third are 20-byte binary values.  The fourth and fifth are
strings; 'by' describes the source of the entry and 'path' tells you where
the data being logged was found.  If the data was a document, the path will
be its location in the file system, key its SHA1 content hash (SHA3 when
that is available), and nodeID identifies which node delivered the data
to this node.  'by' might be a person's name or the name and version number
of the software creating the data.

In this case if leMsg is an instance of LogEntryMsg it would be convenient
for leMsg to have a method like

	leMsg.set(timestamp, nodeID, key, by, path)

Under the hood this would if necessary create an instance of each field of
the message, then assign the method parameters to each in turn.

Of course this should better be

	LogEntryMsg = MsgFactory('org.xlattice.upax', 'LogEntryMsg')
	leMsg = LogEntryMsg(timestamp, nodeID, key, by, path)
	leMsg.put(chan)

The last command would write the data to the channel.  The reverse
operation, deserialization, would be done using

	LogEntryMsg = MsgFactory('org.xlattice.upax', 'LogEntryMsg')
	leMsg = LogEntryMsg.get(chan)

or

	(timestamp, nodeID, key, by, path) = LogEntryMsg.getValues(chan)

If some fields are optional, we can specify which fields are to be
initialized using keywords like

	leMsg = LogEntryMsg(timestamp=int(time.time()), nodeID=nodeID,
	                    key=key, by=by, path=path)

Where fields are or may be multi-valued, we allow the user to supply
possibly empty lists as parameters.

In this approach it is never necessary to explicitly mention enums
or nested messages.  These are specified in the protocol spec file
either at the top level or within a message specification.

DEFICIENCIES:

1.  For the system to be robust, a protocol should be referenced
by its content hash.

2.  In the current implementation the parameters to makeMsgClass are
the protocol name and a reference to the MsgSpec.  This is quite
insecure.  It can be improved by using the protocol name to access
a file under ./specs and then just passing the message name.  Add an
L mapping the protocol name to a hash value and then using that hash
value to retrieve the protocol from Upax and we are done.
