#!/usr/bin/env python3

# testZoggerySerialization.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
from fieldz.fieldTypes import FieldTypes as F, FieldStr as FS
import fieldz.msgSpec as M
import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msgImpl import makeMsgClass, makeFieldClass, MsgImpl

# PROTOCOLS ---------------------------------------------------------
from zoggeryProtoSpec import ZOGGERY_PROTO_SPEC

BUFSIZE = 16 * 1024
rng = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestZoggerySerialization (unittest.TestCase):

    def setUp(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        p = StringProtoSpecParser(data)   # data should be file-like
        self.sOM = p.parse()     # object model from string serialization

    def tearDown(self):
        pass

    # utility functions #############################################
    def leMsgValues(self):
        """ returns a list """
        timestamp = int(time.time())
        nodeID = [0] * 20
        key = [0] * 20
        length = rng.nextInt32()
        by = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        # let's have some random bytes
        rng.nextBytes(nodeID)
        rng.nextBytes(key)
        # NOTE that this is a list
        return [timestamp, nodeID, key, length, by, path]

    # actual unit tests #############################################

    def testZoggerySerialization(self):
        # XXX These comments are generally out of date.

        # Testing MsgSpec with simple fields.  Verify that getter,
        # putter, lenFunc, and pLenFunc work for the basic types
        # (ie, that they are correctly imported into this reg) and
        # they are work for the newly defined single-msg protoSpec.

        # Use ZOGGERY_PROTO_SPEC

        # parse the protoSpec
        # verify that this adds 1 (msg) + 5 (field count) to the number
        # of entries in getters, putters, etc

        self.assertIsNotNone(self.sOM)
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        self.assertEqual('org.xlattice.zoggery', self.sOM.name)

        self.assertEqual(len(self.sOM.enums), 0)
        self.assertEqual(len(self.sOM.msgs), 1)
        self.assertEqual(len(self.sOM.seqs), 0)

        msgSpec = self.sOM.msgs[0]
        msgName = msgSpec.name
        self.assertEqual('logEntry', msgName)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LogEntryMsg class ------------------------------
        LogEntryMsg = makeMsgClass(self.sOM, msgName)

        # create a message instance ---------------------------------
        values = self.leMsgValues()        # a list of quasi-random values
        leMsg = LogEntryMsg(values)

        # DEBUG
        print("type of LogEntryMsg: ", type(LogEntryMsg))
        print("type of leMsg:       ", type(leMsg))
        # END

        self.assertTrue(isinstance(leMsg, LogEntryMsg))

        (timestamp, key, length, nodeID, by, path) = tuple(values)

        self.assertEqual(msgSpec.name, leMsg.name)
        # we don't have any nested enums or messages

        # XXX FAIL: properties have no len()
        # self.assertEqual(0, len(leMsg.enums))

        # DEBUG
        print("leMsg.enums: ", leMsg.enums)
        # END

        # self.assertEqual(0, len(leMsg.msgs))

        self.assertEqual(6, len(leMsg.fieldClasses))
        self.assertEqual(6, len(leMsg))        # number of fields in instance
        for i in range(len(leMsg)):
            # DEBUG
            print("value %d is %s" % (i, values[i]))

            # FAILS: is a PROPERTY OBJECT
            print("leMsg %d is %s" % (i, leMsg[i].value))
            # END
            self.assertEqual(values[i], leMsg[i].value)         # FAILS

        # verify fields are accessible in the object ----------------
        (timestamp, nodeID, key, length, by, path) = tuple(values)
        self.assertEqual(timestamp, leMsg.timestamp)
        self.assertEqual(nodeID, leMsg.nodeID)
        self.assertEqual(key, leMsg.key)
        self.assertEqual(length, leMsg.length)
        self.assertEqual(by, leMsg.by)
        self.assertEqual(path, leMsg.path)

        # serialize the object to the channel -----------------------
        buf = chan.buffer
        chan.clear()
        n = leMsg.writeStandAlone(chan)
        self.assertEqual(0, n)
        oldPosition = chan.position                     # TESTING flip()
        chan.flip()
        self.assertEqual(oldPosition, chan.limit)      # TESTING flip()
        self.assertEqual(0, chan.position)   # TESTING flip()
        actual = chan.limit

        print("ACTUAL LENGTH OF SERIALIZED OBJECT: %u" % actual)

        # deserialize the channel, making a clone of the message ----
        (readBack, n2) = MsgImpl.read(chan, self.sOM)
        self.assertIsNotNone(readBack)
        self.assertTrue(leMsg.__eq__(readBack))

        # produce another message from the same values --------------
        leMsg2 = LogEntryMsg(values)
        chan2 = Channel(BUFSIZE)
        n = leMsg2.writeStandAlone(chan2)
        chan2.flip()
        (copy2, n3) = LogEntryMsg.read(chan2, self.sOM)
        self.assertTrue(leMsg.__eq__(readBack))
        self.assertTrue(leMsg2.__eq__(copy2))
        self.assertEqual(n, n3)

if __name__ == '__main__':
    unittest.main()
