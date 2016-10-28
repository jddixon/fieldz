#!/usr/bin/env python3

# testZoggerySerialization.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class, MsgImpl

# PROTOCOLS ---------------------------------------------------------
from zoggery_proto_spec import ZOGGERY_PROTO_SPEC

BUFSIZE = 16 * 1024
rng = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestZoggerySerialization (unittest.TestCase):

    def setUp(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        self.str_obj_model = ppp.parse()     # object model from string serialization

    def tearDown(self):
        pass

    # utility functions #############################################
    def le_msg_values(self):
        """ returns a list """
        timestamp = int(time.time())
        node_id = [0] * 20
        key = [0] * 20
        length = rng.next_int32()
        by_ = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        # let's have some random bytes
        rng.next_bytes(node_id)
        rng.next_bytes(key)
        # NOTE that this is a list
        return [timestamp, node_id, key, length, by_, path]

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

        self.assertIsNotNone(self.str_obj_model)
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.zoggery', self.str_obj_model.name)

        self.assertEqual(len(self.str_obj_model.enums), 0)
        self.assertEqual(len(self.str_obj_model.msgs), 1)
        self.assertEqual(len(self.str_obj_model.seqs), 0)

        msg_spec = self.str_obj_model.msgs[0]
        msg_name = msg_spec.name
        self.assertEqual('logEntry', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LogEntryMsg class ------------------------------
        LogEntryMsg = make_msg_class(self.str_obj_model, msg_name)

        # DEBUG
        print("testZoggery: LogEntryMsg is of type ", type(LogEntryMsg))
        # END

        # create a message instance ---------------------------------
        values = self.le_msg_values()        # a list of quasi-random values
        le_msg = LogEntryMsg(values)

        # DEBUG
        print("type of LogEntryMsg: ", type(LogEntryMsg))
        print("type of leMsg:       ", type(le_msg))
        # END

        self.assertTrue(isinstance(le_msg, LogEntryMsg))

        (timestamp, key, length, node_id, by_, path) = tuple(values)

        self.assertEqual(msg_spec.name, le_msg._name)
        # we don't have any nested enums or messages

        # XXX FAIL: properties have no len()
        # self.assertEqual(0, len(leMsg.enums))

        # DEBUG
        print("leMsg.enums: ", le_msg.enums)
        # END

        # self.assertEqual(0, len(leMsg.msgs))

        self.assertEqual(6, len(le_msg.field_classes))
        self.assertEqual(6, len(le_msg))        # number of fields in instance
        for i in range(len(le_msg)):
            # DEBUG
            print("value %d is %s" % (i, values[i]))

            # FAILS: is a PROPERTY OBJECT
            print("leMsg %d is %s" % (i, le_msg[i].value))
            # END
            self.assertEqual(values[i], le_msg[i].value)         # FAILS

        # verify fields are accessible in the object ----------------
        (timestamp, node_id, key, length, by_, path) = tuple(values)
        self.assertEqual(timestamp, le_msg.timestamp)
        self.assertEqual(node_id, le_msg.node_id)
        self.assertEqual(key, le_msg.key)
        self.assertEqual(length, le_msg.length)
        self.assertEqual(by_, le_msg.by_)
        self.assertEqual(path, le_msg.path)

        # serialize the object to the channel -----------------------
        buf = chan.buffer
        chan.clear()
        nnn = le_msg.write_stand_alone(chan)
        self.assertEqual(0, nnn)
        old_position = chan.position                     # TESTING flip()
        chan.flip()
        self.assertEqual(old_position, chan.limit)      # TESTING flip()
        self.assertEqual(0, chan.position)   # TESTING flip()
        actual = chan.limit

        print("ACTUAL LENGTH OF SERIALIZED OBJECT: %u" % actual)

        # deserialize the channel, making a clone of the message ----
        (read_back, nn2) = MsgImpl.read(chan, self.str_obj_model)
        self.assertIsNotNone(read_back)
        self.assertTrue(le_msg.__eq__(read_back))

        # produce another message from the same values --------------
        le_msg2 = LogEntryMsg(values)
        chan2 = Channel(BUFSIZE)
        nnn = le_msg2.write_stand_alone(chan2)
        chan2.flip()
        (copy2, nn3) = LogEntryMsg.read(chan2, self.str_obj_model)
        self.assertTrue(le_msg.__eq__(read_back))
        self.assertTrue(le_msg2.__eq__(copy2))
        self.assertEqual(nnn, nn3)

if __name__ == '__main__':
    unittest.main()
