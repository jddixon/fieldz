# fieldz/upax.protoSpec.py


UPAX_PROTOSPEC = """
# MESSAGE SECTION ###################################################
message hello
 dunno      lString?

message error
 code       vu`Int32
 text       lString?

message ack
 text       lString?

message logEntry
 timestamp  fuInt32         # 0: seconds from epoch
 key        fBytes20        # 1: content key
 length     vuInt32         # 2
 nodeID     fBytes20        # 3:
 src        lString         # 4: arbitrary contents; ASCII or unicode
 path       lString         # 5: POSIX path using / as separator

message     keepAlive       # what I would prefer is just an empty message
 text       lString?

message ok                  # empty message better
 text       lString?

bye
 text       lString?

# These define what constitutes an acceptable upax message sequence
seq
 # client           server reply

 hello     :        ack | error .
 keepAlive :        ok
 logEntry  :        ok | error .
 bye       :        ok .

# In the event of a timeout, the connection is just closed.  Either side
# can do this.
"""
