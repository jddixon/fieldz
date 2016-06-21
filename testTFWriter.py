#!/usr/bin/env python3

# testTFWriter.py
import time
import unittest

from rnglib import SimpleRNG

import fieldz.fieldTypes as F
from fieldz.typed import *
from fieldz.msgSpec import *
from fieldz.tfbuffer import *

# scratch variables
b128 = bytearray(16)
b160 = bytearray(20)
b256 = bytearray(32)

# msgSpec -----------------------------------------------------------
#protocol= 'org.xlattice.upax'
name = 'testMsgSpec'
# no enum is used

# XXX MISSING reg; BUT DO WE REALLY WANT FIELD NAMES IN THE REGISTRY?

fields = [

    FieldSpec('i32', F.ndx('vuInt32'), Q_REQUIRED, 0),
    FieldSpec('i32bis', F.ndx('vuInt32'), Q_REQUIRED, 1),
    FieldSpec('i64', F.ndx('vuInt64'), Q_REQUIRED, 2),
    FieldSpec('si32', F.ndx('vsInt32'), Q_REQUIRED, 3),
    FieldSpec('si32bis', F.ndx('vsInt32'), Q_REQUIRED, 4),
    FieldSpec('si64', F.ndx('vsInt64'), Q_REQUIRED, 5),
    FieldSpec('vuint32', F.ndx('vuInt32'), Q_REQUIRED, 6),
    FieldSpec('vuint64', F.ndx('vuInt64'), Q_REQUIRED, 7),
    # take care with gaps from here
    FieldSpec('fint32', F.ndx('vuInt32'), Q_REQUIRED, 8),
    FieldSpec('fint64', F.ndx('vuInt64'), Q_REQUIRED, 9),
    FieldSpec('lstr', F.ndx('lString'), Q_REQUIRED, 10),
    FieldSpec('lbytes', F.ndx('lBytes'), Q_REQUIRED, 11),
    FieldSpec('lbytes16', F.ndx('fBytes16'), Q_REQUIRED, 12),
    FieldSpec('lbytes20', F.ndx('fBytes20'), Q_REQUIRED, 13),
    FieldSpec('lbytes32', F.ndx('fBytes32'), Q_REQUIRED, 14),
]
testMsgSpec = MsgSpec(name, fields)

# -------------------------------------------------------------------


class TestTFWriter (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpBuffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    # actual unit tests #############################################

    # these two methods are all that's left of testTFBuffer.py
    def testBufferCtor(self):
        BUFSIZE = 1024
        buffer = [0] * BUFSIZE
        tfBuf = TFBuffer(testMsgSpec, BUFSIZE, buffer)
        self.assertEqual(0, tfBuf.position)
        self.assertEqual(BUFSIZE, tfBuf.capacity)

    def testBufferCreator(self):
        BUFSIZE = 1024
        tfBuf = TFBuffer.create(testMsgSpec, BUFSIZE)
        self.assertTrue(isinstance(tfBuf, TFBuffer))
        self.assertEqual(0, tfBuf.position)
        self.assertEqual(BUFSIZE, tfBuf.capacity)

    # and these two methods are all that's left of testTFReader.py
    def testReaderCtor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tfReader = TFReader(testMsgSpec, BUFSIZE, buffer)
        self.assertEqual(0, tfReader.position)
        self.assertEqual(BUFSIZE, tfReader.capacity)
        self.assertEqual(BUFSIZE, len(tfReader.buffer))

    def testReaderCreator(self):
        BUFSIZE = 1024
        tfReader = TFReader.create(testMsgSpec, BUFSIZE)
        self.assertTrue(isinstance(tfReader, TFReader))
        self.assertEqual(0, tfReader.position)
        self.assertEqual(BUFSIZE, tfReader.capacity)

    # next two are specific to TFWriter
    def testWriterCtor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tfWriter = TFWriter(testMsgSpec, BUFSIZE, buffer)
        self.assertEqual(0, tfWriter.position)
        self.assertEqual(BUFSIZE, tfWriter.capacity)

    def testWriterCreator(self):
        BUFSIZE = 1024
        tfWriter = TFWriter.create(testMsgSpec, BUFSIZE)
        self.assertTrue(isinstance(tfWriter, TFWriter))
        self.assertEqual(0, tfWriter.position)
        self.assertEqual(BUFSIZE, tfWriter.capacity)

    def doRoundTripField(self, writer, reader, n, fType, value):
        writer.putNext(n, value)
#       # DEBUG
#       tfBuf   = writer.buffer
#       print "after put buffer is " ,
#       self.dumpBuffer(tfBuf)
#       # END
        reader.getNext()
        self.assertEqual(n, reader.fieldNbr)
        # XXX THIS SHOULD WORK:
        # self.assertEqual( fType, reader.fType    )
        self.assertEqual(value, reader.value)
        return n + 1

    def testWritingAndReading(self):
        BUFSIZE = 16 * 1024
        tfWriter = TFWriter.create(testMsgSpec, BUFSIZE)
        tfBuf = tfWriter.buffer       # we share the buffer
        tfReader = TFReader(testMsgSpec, BUFSIZE, tfBuf)

        n = 0                           # 0-based field number

        # field types encoded as varints (8) ========================
        # These are tested in greater detail in testVarint.py; the
        # tests here are to exercise their use in a heterogeneous
        # buffer

        # fields 0: _V_UINT32
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vuInt32', 0x1f)
        self.assertEqual(1, n)         # DEBUG XXX

        # fields 1: _V_UINT32
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vuInt32', 0x172f3e4d)

        # field 2:  _V_UINT64
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vuInt64',
                                  0x12345678abcdef3e)

        # field 3: vsInt32
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vsInt32', 192)

        # field 4: vsInt32
        # _V_SINT32 (zig-zag encoded, optimal for small values near zero)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vsInt32', -192)

        # field 5: _V_SINT64
        n = self.doRoundTripField(
            tfWriter, tfReader, n, 'vsInt64', -193)  # GEEP

        # field 6: _V_UINT32
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vuInt32',
                                  0x172f3e4d)
        # field 7: _V_UINT64
        n = self.doRoundTripField(tfWriter, tfReader, n, 'vuInt64',
                                  0xffffffff172f3e4d)

        # _V_BOOL
        # XXX NOT IMPLEMENTED, NOT TESTED

        # _V_ENUM
        # XXX NOT IMPLEMENTED, NOT TESTED

        # encoded as fixed length 32 bit fields =====================
        # field 8: _F_INT32
        n = self.doRoundTripField(tfWriter, tfReader, n, 'fInt32',
                                  0x172f3e4d)
        # _F_FLOAT
        # XXX STUB XXX not implemented

        # encoded as fixed length 64 bit fields =====================
        # field 9: _F_INT64
        n = self.doRoundTripField(tfWriter, tfReader, n, 'fInt64',
                                  0xffffffff172f3e4d)
        # _F_DOUBLE
        # XXX STUB XXX not implemented

        # encoded as varint len followed by byte[len] ===============
        # field 10: _L_STRING
        s = self.rng.nextFileName(16)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'lString', s)

        # field 11: _L_BYTES
        b = bytearray(8 + self.rng.nextInt16(16))
        self.rng.nextBytes(b)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'lBytes', b)

        # _L_MSG
        # XXX STUB XXX not implemented

        # fixed length byte sequences, byte[N} ======================
        # field 12: _F_BYTES16
        self.rng.nextBytes(b128)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'fBytes16', b128)

        # field 13: _F_BYTES20
        self.rng.nextBytes(b160)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'fBytes20', b160)

        # may want to introduce eg fNodeID20 and fSha1Key types
        # field 14: _F_BYTES32
        self.rng.nextBytes(b256)
        n = self.doRoundTripField(tfWriter, tfReader, n, 'fBytes32', b256)

        # may want to introduce eg fSha3Key type, allowing semantic checks

if __name__ == '__main__':
    unittest.main()
