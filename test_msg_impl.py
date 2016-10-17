#!/usr/bin/env python3

# testMsgImpl.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
import fieldz.field_types as F
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msg_impl import makeMsgClass, makeFieldClass, MsgImpl
# XXX NEEDS FIXING: we shouldn't be using this low-level code
from fieldz.raw import writeFieldHdr, writeRawVarint, LEN_PLUS_TYPE

#################################################################
# THIS WAS HACKED FROM testProtoSpec.py; CAN HACK MORE FROM THERE
#################################################################

# PROTOCOLS ---------------------------------------------------------
from little_big_test import LITTLE_BIG_PROTO_SPEC

from simple_protocol import SIMPLE_PROTOCOL
from zoggery_proto_spec import ZOGGERY_PROTO_SPEC
from nested_enum_proto_spec import NESTED_ENUM_PROTO_SPEC
from nested_msgs_proto_spec import NESTED_MSGS_PROTO_SPEC

BUFSIZE = 16 * 1024
rng = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestMsgImpl (unittest.TestCase):

    def setUp(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        p = StringProtoSpecParser(data)   # data should be file-like
        self.assertTrue(p is not None)
        self.sOM = p.parse()     # object model from string serialization
        self.assertTrue(self.sOM is not None)
        self.protoName = self.sOM.name  # the dotted name of the protocol
        # DEBUG
        print("setUp: proto name is %s" % self.protoName)
        # END

    def tearDown(self):
        pass

    # utility functions #############################################
    def leMsgValues(self):
        """ returns a list """
        timestamp = int(time.time())
        nodeID = [0] * 20
        key = [0] * 20
        length = rng.nextInt32(256 * 256)
        # let's have some random bytes
        rng.nextBytes(nodeID)
        rng.nextBytes(key)
        by = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        return [timestamp, nodeID, key, length, by, path]

    # NOT YET USED HERE
    def littleBigValues(self):
        values = []
        # XXX these MUST be kept in sync with littleBigTest.py
        values.append(rng.nextBoolean())       # vBoolReqField
        values.append(rng.nextInt16())         # vEnumReqField

        values.append(rng.nextInt32())         # vuInt32ReqField
        values.append(rng.nextInt32())         # vuInt64ReqField
        values.append(rng.nextInt64())         # vsInt32ReqField
        values.append(rng.nextInt64())         # vsInt64ReqField

        # #vuInt32ReqField
        # #vuInt64ReqField

        values.append(rng.nextInt32())         # fsInt32ReqField
        values.append(rng.nextInt32())         # fuInt32ReqField
        values.append(rng.nextReal())          # fFloatReqField

        values.append(rng.nextInt64())         # fsInt64ReqField
        values.append(rng.nextInt64())         # fuInt64ReqField
        values.append(rng.nextReal())          # fDoubleReqField

        values.append(rng.nextFileName(16))    # lStringReqField

        rndLen = 16 + rng.nextInt16(49)
        byteBuf = bytearray(rndLen)
        values.append(rng.nextBytes(byteBuf))  # lBytesReqField

        b128Buf = bytearray(16)
        values.append(rng.nextBytes(b128Buf))  # fBytes16ReqField

        b160Buf = bytearray(20)
        values.append(rng.nextBytes(b160Buf))  # fBytes20ReqField

        b256Buf = bytearray(32)
        values.append(rng.nextBytes(b256Buf))  # fBytes32ReqField  GEEP

    # actual unit tests #############################################
    def checkFieldImplAgainstSpec(self, protoName, msgName, fieldSpec, value):
        self.assertIsNotNone(fieldSpec)
        dottedName = "%s.%s" % (protoName, msgName)
        Clz = makeFieldClass(dottedName, fieldSpec)
        if '__dict__' in dir(Clz):
            print('\nGENERATED FieldImpl CLASS DICTIONARY')
            for e in list(Clz.__dict__.keys()):
                print("%-20s %s" % (e, Clz.__dict__[e]))

        self.assertIsNotNone(Clz)
        f = Clz(value)
        self.assertIsNotNone(f)

        # instance attributes -----------------------------
        self.assertEqual(fieldSpec.name, f._name)
        self.assertEqual(fieldSpec.fTypeNdx, f.fType)
        self.assertEqual(fieldSpec.quantifier, f.quantifier)
        self.assertEqual(fieldSpec.fieldNbr, f.fieldNbr)
        self.assertIsNone(f.default)          # not an elegant test

        # instance attribute ------------------------------
        self.assertEqual(value, f.value)

        # with slots enabled, this is never seen ----------
        # because __dict__ is not in the list of valid
        # attributes for f
        if '__dict__' in dir(f):
            print('\nGENERATED FieldImpl INSTANCE DICTIONARY')
            for item in list(f.__dict__.keys()):
                print("%-20s %s" % (item, f.__dict__[item]))     # GEEP

    def testFieldImpl(self):
        msgSpec = self.sOM.msgs[0]

        # the fields in this imaginary logEntry
        values = self.leMsgValues()

        for i in range(len(msgSpec)):
            print(
                "\nDEBUG: field %u ------------------------------------------------------" %
                i)
            fieldSpec = msgSpec[i]
            self.checkFieldImplAgainstSpec(
                self.protoName, msgSpec.name, fieldSpec, values[i])

    def testCaching(self):
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        msgSpec = self.sOM.msgs[0]
        name = msgSpec.name
        Clz0 = makeMsgClass(self.sOM, name)
        Clz1 = makeMsgClass(self.sOM, name)
        # we cache classe, so the two should be the same
        self.assertEqual(id(Clz0), id(Clz1))

        # chan    = Channel(BUFSIZE)
        values = self.leMsgValues()
        leMsg0 = Clz0(values)
        leMsg1 = Clz0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(leMsg0), id(leMsg1))

        fieldSpec = msgSpec[0]
        dottedName = "%s.%s" % (self.protoName, msgSpec.name)
        F0 = makeFieldClass(dottedName, fieldSpec)
        F1 = makeFieldClass(dottedName, fieldSpec)
        self.assertEqual(id(F0), id(F1))           # GEEP

    def testMsgImpl(self):
        self.assertIsNotNone(self.sOM)
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        self.assertEqual('org.xlattice.zoggery', self.sOM.name)

        self.assertEqual(0, len(self.sOM.enums))
        self.assertEqual(1, len(self.sOM.msgs))
        self.assertEqual(0, len(self.sOM.seqs))

        msgSpec = self.sOM.msgs[0]

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LogEntryMsg class ------------------------------

        LogEntryMsg = makeMsgClass(self.sOM, msgSpec.name)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes

        # TEST TEMPORARILY DISABLED
#        try:
#            LogEntryMsg.foo = 42
#            self.fail(
#                "ERROR: attempt to assign new class attribute succeeded")
#        except AttributeError as ae:
#
#            # DEBUG
#            print(
#                "success: attr error attempting to set LogEntryMsg.foo: " +
#                str(ae))
#            # END
#            pass                # GEEP

        # create a message instance ---------------------------------
        values = self.leMsgValues()            # quasi-random values
        leMsg = LogEntryMsg(values)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes.  This works at the class level but
        # NOT at the instance level
        if False:
            try:
                leMsg.foo = 42
                self.fail(
                    "ERROR: attempt to assign new instance attribute succeeded")
            except AttributeError as ae:
                # DEBUG
                print("ATTR ERROR ATTEMPTING TO SET leMsg.foo: " + str(ae))
                # END
                pass

        # leMsg._name is a property
        # TEST TEMPORARILY DISABLED
#        try:
#            leMsg._name = 'boo'
#            self.fail("ERROR: attempt to change message name succeeded")
#        except AttributeError:
#            pass

        self.assertEqual(msgSpec.name, leMsg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(leMsg.enums))
        self.assertEqual(0, len(leMsg.msgs))

        self.assertEqual(6, len(leMsg.fieldClasses))
        self.assertEqual(6, len(leMsg))        # number of fields in instance
        # TEST TEMPORARILY DISABLED
#        for i in range(len(leMsg)):
#            self.assertEqual(values[i], leMsg[i].value)

        ################################
        # XXX FIELDS ARE NOT AS EXPECTED
        ################################

        # verify fields are accessible in the object ----------------
        # DEBUG
        for field in leMsg._fieldClasses:
            print("FIELD: %s = %s " % (field._name, field.value))
        # END
        (timestamp, nodeID, key, length, by, path) = tuple(values)
        self.assertEqual(timestamp, leMsg.timestamp)    # FAILS: null timestamp

        self.assertEqual(nodeID, leMsg.nodeID)
        self.assertEqual(key, leMsg.key)
        self.assertEqual(length, leMsg.length)
        self.assertEqual(by, leMsg.by)
        self.assertEqual(path, leMsg.path)

        # serialize the object to the channel -----------------------
        # XXX not a public method
        expectedMsgLen = leMsg._wireLen()
        print("EXPECTED LENGTH OF SERIALIZED OBJECT: %u" % expectedMsgLen)
        buf = chan.buffer

        chan.clear()

        n = leMsg.writeStandAlone(chan)                 # n is class index
        oldPosition = chan.position                     # TESTING flip()
        chan.flip()
        self.assertEqual(oldPosition, chan.limit)      # TESTING flip()
        self.assertEqual(0, chan.position)   # TESTING flip()
        actual = chan.limit

        # deserialize the channel, making a clone of the message ----
        # XXX FAILS BECAUSE HEADER IS PRESENT:
        #(readBack,n2) = LogEntryMsg.read(chan, self.sOM)
        (readBack, n2) = MsgImpl.read(chan, self.sOM)
        self.assertIsNotNone(readBack)
        self.assertTrue(leMsg.__eq__(readBack))
        self.assertEqual(n, n2)

        # produce another message from the same values --------------
        leMsg2 = LogEntryMsg(values)
        chan2 = Channel(BUFSIZE)
        n = leMsg2.writeStandAlone(chan2)
        chan2.flip()
        (copy2, n3) = LogEntryMsg.read(chan2, self.sOM)
        self.assertTrue(leMsg.__eq__(copy2))
        self.assertTrue(leMsg2.__eq__(copy2))

#   def testMsg(self):
#       # Testing MsgSpec with simple fields.  Verify that read,
#       # putter, lenFunc, and pLenFunc work for the basic types
#       # (ie, that they are correctly imported into this reg) and
#       # they are work for the newly defined single-msg protoSpec.

#       # Use ZOGGERY_PROTO_SPEC

#       # parse the protoSpec
#       # verify that this adds 1 (msg) + 5 (field count) to the number
#       # of entries in getters, putters, etc

#       pass

#   def testEnum(self):
#       # need to verify that getter, putter, lenFunc, and pLenFunc work
#       # for enums and nested enums

#       # Use NESTED_ENUM_PROTO_SPEC
#       # XXX STUB XXX

#       pass

#   def testNestedMsgs(self):
#       # Test MsgSpec with embedded msg and enum fields, to a depth of
#       # at least 3.  Need to verify that getter, putter, lenFunc, and
#       # pLenFunc work.

#       # Use NESTED_MSGS_PROTO_SPEC
#       # XXX STUB XXX

#       pass    # GEEP

if __name__ == '__main__':
    unittest.main()
