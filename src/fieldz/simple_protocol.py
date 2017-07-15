SIMPLE_PROTOCOL = """
protocol org.xlattice.fieldz.test.A

# We require (at least for the moment) that enums come first or
# not at all, except that nested enumSpecs and msgSpecs will need
# to be supported.

# yes, I'm playing around
enum OK
 ok          1

enum ErrorCode
 # we can see that this could easily be a list of pairs,
 # with each code matched with a predefined string text
 NotFound    2       # ENOENT
 IOError     5       # EIO
 TryAgain    11      # EAGAIN
 Busy        16      # EBUSY
 Exists      17      # EEXIST
 InvalidArg  22      # EINVAL
 TooBig      27      # EFBIG
 OutOfRange  33      # EDOM, math arg out of domain of func

message hello
 myNodeID    fbytes20
 myRSAPubKey lbytes? # if present, client's RSA public key

message logEntry
 timestamp   fuint32
 key         fbytes20
 length      vuint32
 nodeID      fbytes20
 src         lstring         # arbitrary text, whodunnit
 path        lstring         # UNIX-style

message errorMsg
 code        ErrorCode
 text        lstring

message get
 key         fbytes20

message put
 src         fbytes20?       # 20 byte nodeID: where the data came from
 dest        fbytes20?       # if present, means forward to this nodeID
 key         fbytes20        # SHA1 hash of content
 content     lbytes

message ok
 code        OK              # the enum has only one possible value

message keepAlive
 # no fields

message ack
 # no fields

# the left side specifies what the client can send, the right side the
# server's permitted replies
seq
 hello:      ack | errorMsg
 logEntry:   ok  | errorMsg
 get:        put | errorMsg
 put:        ok  | errorMsg
 keepAlive:  ok

"""
# END TEST DATA
