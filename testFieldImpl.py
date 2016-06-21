#!/usr/bin/env python3

# ~/dev/py/fieldz/testFieldImpl.py

import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

#from fieldz.parser import StringProtoSpecParser
import fieldz.fieldTypes as F
import fieldz.msgSpec as M
#import fieldz.typed as T
import fieldz.reg as R

from fieldz.fieldImpl import makeFieldClass

#from fieldz.chan import Channel
#from fieldz.msgImpl import makeMsgClass, makeFieldClass, MsgImpl
#from fieldz.raw import writeFieldHdr, writeRawVarint, LEN_PLUS_TYPE

PROTOCOL_UNDER_TEST = 'org.xlattice.fieldz.test.fieldSpec'
MSG_UNDER_TEST = 'myTestMsg'

BUFSIZE = 16 * 1024


class TestFieldImpl (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

#       data = StringIO(ZOGGERY_PROTO_SPEC)
#       p = StringProtoSpecParser(data)   # data should be file-like
#       self.sOM = p.parse()     # object model from string serialization
#       self.protoName = self.sOM.name  # the dotted name of the protocol

    def tearDown(self):
        pass

    # utility functions #############################################

    def makeRegistries(self, protocol):
        nodeReg = R.NodeReg()
        protoReg = R.ProtoReg(protocol, nodeReg)
        msgReg = R.MsgReg(protoReg)
        return (nodeReg, protoReg, msgReg)

    def leMsgValues(self):
        """ returns a list """
        timestamp = int(time.time())
        nodeID = [0] * 20
        key = [0] * 20
        length = self.rng.nextInt32(256 * 256)
        # let's have some random bytes
        self.rng.nextBytes(nodeID)
        self.rng.nextBytes(key)
        by = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        return [timestamp, nodeID, key, length, by, path]

    def lilBigMsgValues(self):
        """
        This returns a list of random-ish values in order by field type
        so that values[_F_FLOAT], for example, is a random float value.
        """
        values = []

        # 2016-03-30 This is NOT in sync with littleBigTest.py,
        #   because I have added a None for lMsg at _L_MSG

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

        values.append(None)                         # <-------------- for lMsg

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

    def checkFieldImplAgainstSpec(self,
                                  protoName, msgName,             # not actually tested
                                  fieldSpec, value):              # significant for tests

        self.assertIsNotNone(fieldSpec)
        dottedName = "%s.%s" % (protoName, msgName)
        Clz = makeFieldClass(dottedName, fieldSpec)         # a class
#       if '__dict__' in dir(Clz):
#           print('\nGENERATED FieldImpl CLASS DICTIONARY')
#           for e in list(Clz.__dict__.keys()):
#               print("%-20s %s" % (e, Clz.__dict__[e]))

        self.assertIsNotNone(Clz)
        f = Clz(value)                                      # an instance
        self.assertIsNotNone(f)
        self.assertTrue(isinstance(f, Clz))

        # instance attributes -----------------------------
        # we verify that the properties work correctly

        self.assertEqual(fieldSpec.name, f.name)
        self.assertEqual(fieldSpec.fTypeNdx, f.fType)
        self.assertEqual(fieldSpec.quantifier, f.quantifier)
        self.assertEqual(fieldSpec.fieldNbr, f.fieldNbr)
        self.assertIsNone(f.default)          # not an elegant test

        # instance attribute ------------------------------
        # we can read back the value assigned to the instance

        self.assertEqual(value, f.value)

        # with slots enabled, this is never seen ----------
        # because __dict__ is not in the list of valid
        # attributes for f
#       if '__dict__' in dir(f):
#           print('\nGENERATED FieldImpl INSTANCE DICTIONARY')
#           for item in list(f.__dict__.keys()):
#               print("%-20s %s" % (item, f.__dict__[item]))

    def testFieldImpl(self):

        nodeReg, protoReg, msgReg = self.makeRegistries(PROTOCOL_UNDER_TEST)
        values = self.lilBigMsgValues()

        # There are 18 values corresponding to the 18 field types;
        # _L_MSG should be skipped

        for t in range(F._F_BYTES32 + 1):
            if t == F._L_MSG:
                continue

            # default quantifier is Q_REQ_, default is None

            fieldName = 'field%d' % t
            fieldSpec = M.FieldSpec(msgReg, fieldName, t, fieldNbr=t + 100)

            self.checkFieldImplAgainstSpec(
                PROTOCOL_UNDER_TEST, MSG_UNDER_TEST,
                fieldSpec, values[t])

    # TEST FIELD SPEC -----------------------------------------------

    def doFieldSpecTest(self, name, fType, quantifier=M.Q_REQUIRED,
                        fieldNbr=0, default=None):

        nodeReg, protoReg, msgReg = self.makeRegistries(PROTOCOL_UNDER_TEST)

        # XXX Defaults are ignored for now.
        f = M.FieldSpec(msgReg, name, fType, quantifier, fieldNbr, default)

        self.assertEqual(name, f.name)
        self.assertEqual(fType, f.fTypeNdx)
        self.assertEqual(quantifier, f.quantifier)
        self.assertEqual(fieldNbr, f.fieldNbr)
        if default is not None:
            self.assertEqual(default, f.default)

        expectedRepr = "%s %s%s @%d \n" % (
            name, f.fTypeName, M.qName(quantifier), fieldNbr)
        # DEFAULTS NOT SUPPORTED
        self.assertEqual(expectedRepr, f.__repr__())

    def testsQuantifiers(self):
        qName = M.qName
        self.assertEqual('', qName(M.Q_REQUIRED))
        self.assertEqual('?', qName(M.Q_OPTIONAL))
        self.assertEqual('*', qName(M.Q_STAR))
        self.assertEqual('+', qName(M.Q_PLUS))

    def testFieldSpec(self):
        # default is not implemented yet
        self.doFieldSpecTest('foo', F._V_UINT32, M.Q_REQUIRED, 9)
        self.doFieldSpecTest('bar', F._V_SINT32, M.Q_STAR, 17)
        self.doFieldSpecTest('nodeID', F._F_BYTES20, M.Q_OPTIONAL, 92)
        self.doFieldSpecTest('tix', F._V_BOOL, M.Q_PLUS, 147)


if __name__ == '__main__':
    unittest.main()
