# fieldz/upax.protoSpec.py


UPAX_PROTOSPEC = """
# MESSAGE SECTION ###################################################
message hello
 dunno      lstring?

message error
 code       vuint32
 text       lstring?

message ack
 text       lstring?

message logEntry
 timestamp  fuint32         # 0: seconds from epoch
 key        fbytes20        # 1: content key
 length     vuint32         # 2
 nodeID     fbytes20        # 3:
 src        lstring         # 4: arbitrary contents; ASCII or unicode
 path       lstring         # 5: POSIX path using / as separator

message     keepAlive       # what I would prefer is just an empty message
 text       lstring?

message ok                  # empty message better
 text       lstring?

bye
 text       lstring?

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
