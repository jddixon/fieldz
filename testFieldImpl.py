#!/usr/bin/python3

# ~/dev/py/fieldz/testFieldImpl.py

import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

#from fieldz.parser import StringProtoSpecParser
#import fieldz.fieldTypes as F
#import fieldz.msgSpec as M
#import fieldz.typed as T
#from fieldz.chan import Channel
#from fieldz.msgImpl import makeMsgClass, makeFieldClass, MsgImpl
#from fieldz.raw import writeFieldHdr, writeRawVarint, LEN_PLUS_TYPE

BUFSIZE = 16 * 1024
rng = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestFieldImpl (unittest.TestCase):

    def setUp(self):
        pass

#       data = StringIO(ZOGGERY_PROTO_SPEC)
#       p = StringProtoSpecParser(data)   # data should be file-like
#       self.sOM = p.parse()     # object model from string serialization
#       self.protoName = self.sOM.name  # the dotted name of the protocol

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

#   def littleBigValues(self):
#       values = []
#       # XXX these MUST be kept in sync with littleBigTest.py
#       values.append(rng.nextBoolean())       # vBoolReqField
#       values.append(rng.nextInt16())         # vEnumReqField
#
#       values.append(rng.nextInt32())         # vuInt32ReqField
#       values.append(rng.nextInt32())         # vuInt64ReqField
#       values.append(rng.nextInt64())         # vsInt32ReqField
#       values.append(rng.nextInt64())         # vsInt64ReqField

#           # #vuInt32ReqField
#           # #vuInt64ReqField
#
#       values.append(rng.nextInt32())         # fsInt32ReqField
#       values.append(rng.nextInt32())         # fuInt32ReqField
#       values.append(rng.nextReal())          # fFloatReqField
#
#       values.append(rng.nextInt64())         # fsInt64ReqField
#       values.append(rng.nextInt64())         # fuInt64ReqField
#       values.append(rng.nextReal())          # fDoubleReqField
#
#       values.append(rng.nextFileName(16))    # lStringReqField

#       rndLen = 16 + rng.nextInt16(49)
#       byteBuf = bytearray(rndLen)
#       values.append(rng.nextBytes(byteBuf))  # lBytesReqField

#       b128Buf = bytearray(16)
#       values.append(rng.nextBytes(b128Buf))  # fBytes16ReqField

#       b160Buf = bytearray(20)
#       values.append(rng.nextBytes(b160Buf))  # fBytes20ReqField

#       b256Buf = bytearray(32)
#       values.append(rng.nextBytes(b256Buf))  # fBytes32ReqField  GEEP

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
        pass

#   def testCaching(self):
#       self.assertTrue(isinstance(self.sOM, M.ProtoSpec))
#       msgSpec = self.sOM.msgs[0]
#       name = msgSpec.name
#       Clz0 = makeMsgClass(self.sOM, name)
#       Clz1 = makeMsgClass(self.sOM, name)
#       # we cache classe, so the two should be the same
#       self.assertEqual(id(Clz0), id(Clz1))

#       # chan    = Channel(BUFSIZE)
#       values = self.leMsgValues()
#       leMsg0 = Clz0(values)
#       leMsg1 = Clz0(values)
#       # we don't cache instances, so these will differ
#       self.assertNotEquals(id(leMsg0), id(leMsg1))

#       fieldSpec = msgSpec[0]
#       dottedName = "%s.%s" % (self.protoName, msgSpec.name)
#       F0 = makeFieldClass(dottedName, fieldSpec)
#       F1 = makeFieldClass(dottedName, fieldSpec)
#       self.assertEqual(id(F0), id(F1))           # GEEP


if __name__ == '__main__':
    unittest.main()
