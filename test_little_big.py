#!/usr/bin/env python3

# testLittleBig.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

# XXX FAILS to import write if named 'putter':
from fieldz.msg_impl import makeMsgClass,  \
    makeFieldClass

from fieldz.parser import StringProtoSpecParser
import fieldz.field_types as F
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel

#################################################################
# THIS WAS HACKED FROM testProtoSpec.py; CAN HACK MORE FROM THERE
#################################################################

# PROTOCOLS ---------------------------------------------------------
from little_big_test import LITTLE_BIG_PROTO_SPEC

BUFSIZE = 16 * 1024

# TESTS -------------------------------------------------------------


class TestLittleBig (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())
        data = StringIO(LITTLE_BIG_PROTO_SPEC)
        p = StringProtoSpecParser(data)   # data should be file-like
        self.sOM = p.parse()     # object model from string serialization
        self.protoName = self.sOM.name  # the dotted name of the protocol

    def tearDown(self):
        pass

    # utility functions #############################################

    def lilBigMsgValues(self):
        values = []
        # XXX these MUST be kept in sync with littleBigTest.py
        values.append(self.rng.nextBoolean())       # vBoolReqField
        values.append(self.rng.nextInt16())         # vEnumReqField

        values.append(self.rng.nextInt32())         # vuInt32ReqField
        values.append(self.rng.nextInt32())         # vuInt64ReqField
        values.append(self.rng.nextInt64())         # vsInt32ReqField
        values.append(self.rng.nextInt64())         # vsInt64ReqField

        # #vuInt32ReqField
        # #vuInt64ReqField

        values.append(self.rng.nextInt32())         # fsInt32ReqField
        values.append(self.rng.nextInt32())         # fuInt32ReqField
        values.append(self.rng.nextReal())          # fFloatReqField

        values.append(self.rng.nextInt64())         # fsInt64ReqField
        values.append(self.rng.nextInt64())         # fuInt64ReqField
        values.append(self.rng.nextReal())          # fDoubleReqField

        values.append(self.rng.nextFileName(16))    # lStringReqField

        rndLen = 16 + self.rng.nextInt16(49)
        byteBuf = bytearray(rndLen)
        self.rng.nextBytes(byteBuf)
        values.append(bytes(byteBuf))               # lBytesReqField

        b128Buf = bytearray(16)
        self.rng.nextBytes(b128Buf)
        values.append(bytes(b128Buf))               # fBytes16ReqField

        b160Buf = bytearray(20)
        self.rng.nextBytes(b160Buf)
        values.append(bytes(b160Buf))               # fBytes20ReqField

        b256Buf = bytearray(32)
        self.rng.nextBytes(b256Buf)
        values.append(bytes(b256Buf))               # fBytes32ReqField

        return values

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

        # class attributes --------------------------------
        self.assertEqual(fieldSpec.name, f.name)
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
        values = self.lilBigMsgValues()

        for i in range(len(msgSpec)):
            print(
                "\nDEBUG: field %u ------------------------------------------------------" %
                i)
            fieldSpec = msgSpec[i]
            self.checkFieldImplAgainstSpec(
                self.protoName, msgSpec.name, fieldSpec, values[i])

    def testCaching(self):
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        # XXX A HACK WHILE WE CHANGE INTERFACE ------------
        msgSpec = self.sOM.msgs[0]
        name = msgSpec.name

        Clz0 = makeMsgClass(self.sOM, name)
        # DEBUG
        print("Constructed Clz0 name is '%s'" % Clz0.name)
        # END
        self.assertEqual(name, Clz0.name)
        Clz1 = makeMsgClass(self.sOM, name)
        self.assertEqual(name, Clz1.name)

        # END HACK ----------------------------------------
        # we cache classe, so the two should be the same
        self.assertEqual(id(Clz0), id(Clz1))

        # chan    = Channel(BUFSIZE)
        values = self.lilBigMsgValues()
        lilBigMsg0 = Clz0(values)
        lilBigMsg1 = Clz0(values)
        # we don't cache instances, so these will differ
        self.assertNotEquals(id(lilBigMsg0), id(lilBigMsg1))

        fieldSpec = msgSpec[0]
        dottedName = "%s.%s" % (self.protoName, msgSpec.name)
        F0 = makeFieldClass(dottedName, fieldSpec)
        F1 = makeFieldClass(dottedName, fieldSpec)
        self.assertEqual(id(F0), id(F1))

    def testLittleBig(self):
        self.assertIsNotNone(self.sOM)
        self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
        self.assertEqual('org.xlattice.fieldz.test.littleBigProto',
                         self.sOM.name)

        self.assertEqual(0, len(self.sOM.enums))
        self.assertEqual(1, len(self.sOM.msgs))
        self.assertEqual(0, len(self.sOM.seqs))

        msgSpec = self.sOM.msgs[0]

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LittleBigMsg class ------------------------------
        LittleBigMsg = makeMsgClass(self.sOM, msgSpec.name)

        # -------------------------------------------------------------
        # XXX the following fails because field 2 is seen as a property
        # instead of a list
        if False:        # DEBUGGING
            print('\nLittleBigMsg CLASS DICTIONARY')
            for (ndx, key) in enumerate(LittleBigMsg.__dict__.keys()):
                print("%3u: %-20s %s" % (ndx, key, LittleBigMsg.__dict__[key]))
        # -------------------------------------------------------------

        # create a message instance ---------------------------------
        values = self.lilBigMsgValues()            # quasi-random values
        lilBigMsg = LittleBigMsg(values)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes.  This works at the class level but
        # NOT at the instance level
        #
        if True:
            try:
                lilBigMsg.foo = 42
                self.fail(
                    "ERROR: attempt to assign new instance attribute succeeded")
            except AttributeError as ae:
                # DEBUG
                print("ATTR ERROR ATTEMPTING TO SET lilBigMsg.foo: " + str(ae))
                # END
                pass

        if '__dict__' in dir(lilBigMsg):
            print('\nlilBigMsg INSTANCE DICTIONARY')
            for e in list(lilBigMsg.__dict__.keys()):
                print("%-20s %s" % (e, lilBigMsg.__dict__[e]))

        # lilBigMsg.name is a property
        try:
            lilBigMsg.name = 'boo'
            self.fail("ERROR: attempt to change message name succeeded")
        except AttributeError:
            pass

        self.assertEqual(msgSpec.name, lilBigMsg.name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(lilBigMsg.enums))
        self.assertEqual(0, len(lilBigMsg.msgs))

        self.assertEqual(17, len(lilBigMsg.fieldClasses))
        self.assertEqual(17, len(lilBigMsg))    # number of fields in instance
        for i in range(len(lilBigMsg)):
            self.assertEqual(values[i], lilBigMsg[i].value)

        # serialize the object to the channel -----------------------
        print("\nDEBUG: PHASE A ######################################")
        n = lilBigMsg.writeStandAlone(chan)

        oldPosition = chan.position
        chan.flip()
        self.assertEqual(oldPosition, chan.limit)
        self.assertEqual(0, chan.position)

        # deserialize the channel, making a clone of the message ----
        (readBack, n2) = LittleBigMsg.read(chan, self.sOM)  # sOM is protoSpec
        self.assertIsNotNone(readBack)
        self.assertEqual(n, n2)

        # verify that the messages are identical --------------------
        self.assertTrue(lilBigMsg.__eq__(readBack))

        print("\nDEBUG: PHASE B ######################################")
        # produce another message from the same values --------------
        lilBigMsg2 = LittleBigMsg(values)
        chan2 = Channel(BUFSIZE)
        n = lilBigMsg2.writeStandAlone(chan2)
        chan2.flip()
        (copy2, n3) = LittleBigMsg.read(chan2, self.sOM)
        self.assertIsNotNone(copy2)
        self.assertEqual(n, n3)
        self.assertTrue(lilBigMsg.__eq__(copy2))
        self.assertTrue(lilBigMsg2.__eq__(copy2))

        # test clear()
        chan2.position = 97
        chan2.limit = 107
        chan2.clear()
        self.assertEqual(0, chan2.limit)
        self.assertEqual(0, chan2.position)

if __name__ == '__main__':
    unittest.main()
