#!/usr/bin/env python3

# testTFWriter.py
import time
import unittest

from rnglib import SimpleRNG

from fieldz.field_types import FieldStr
import fieldz.msg_spec as M
import fieldz.reg as R

# from fieldz.msg_spec import *
from fieldz.msg_spec import (
    Q_REQUIRED  # , Q_OPTIONAL, Q_PLUS, Q_STAR,
    FieldSpec, )
# from fieldz.tfbuffer import *

# scratch variables
b128 = bytearray(16)
b160 = bytearray(20)
b256 = bytearray(32)

# msgSpec -----------------------------------------------------------
protocol = 'org.xlattice.upax'
name = 'test_msg_spec'
node_reg = R.NodeReg()
proto_reg = R.ProtoReg(protocol, node_reg)
msg_reg = R.MsgReg(proto_reg)
parent = M.ProtoSpec(protocol, proto_reg)

# no enum is used

# XXX MISSING reg; BUT DO WE REALLY WANT FIELD NAMES IN THE REGISTRY?

ndx = FieldStr.ndx

fields = [

    FieldSpec(msg_reg, 'i32', ndx('vuint32'), Q_REQUIRED, 0),
    FieldSpec(msg_reg, 'i32bis', ndx('vuint32'), Q_REQUIRED, 1),
    FieldSpec(msg_reg, 'i64', ndx('vuint64'), Q_REQUIRED, 2),
    FieldSpec(msg_reg, 'si32', ndx('vsint32'), Q_REQUIRED, 3),
    FieldSpec(msg_reg, 'si32bis', ndx('vsint32'), Q_REQUIRED, 4),
    FieldSpec(msg_reg, 'si64', ndx('vsint64'), Q_REQUIRED, 5),
    FieldSpec(msg_reg, 'vuint32', ndx('vuint32'), Q_REQUIRED, 6),
    FieldSpec(msg_reg, 'vuint64', ndx('vuint64'), Q_REQUIRED, 7),
    # take care with gaps from here
    FieldSpec(msg_reg, 'fint32', ndx('vuint32'), Q_REQUIRED, 8),
    FieldSpec(msg_reg, 'fint64', ndx('vuint64'), Q_REQUIRED, 9),
    FieldSpec(msg_reg, 'lstr', ndx('lstring'), Q_REQUIRED, 10),
    FieldSpec(msg_reg, 'lbytes', ndx('lbytes'), Q_REQUIRED, 11),
    FieldSpec(msg_reg, 'lbytes16', ndx('fbytes16'), Q_REQUIRED, 12),
    FieldSpec(msg_reg, 'lbytes20', ndx('fbytes20'), Q_REQUIRED, 13),
    FieldSpec(msg_reg, 'lbytes32', ndx('fbytes32'), Q_REQUIRED, 14),
]
test_msg_spec = MsgSpec(name, proto_reg, parent)

# -------------------------------------------------------------------


class TestTFWriter(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    # actual unit tests #############################################

    # these two methods are all that's left of testTFBuffer.py
    def testBufferCtor(self):
        BUFSIZE = 1024
        buffer = [0] * BUFSIZE
        tfBuf = TFBuffer(test_msg_spec, BUFSIZE, buffer)
        self.assertEqual(0, tfBuf.position)
        self.assertEqual(BUFSIZE, tfBuf.capacity)

    def testBufferCreator(self):
        BUFSIZE = 1024
        tfBuf = TFBuffer.create(test_msg_spec, BUFSIZE)
        self.assertTrue(isinstance(tfBuf, TFBuffer))
        self.assertEqual(0, tfBuf.position)
        self.assertEqual(BUFSIZE, tfBuf.capacity)

    # and these two methods are all that's left of testTFReader.py
    def testReaderCtor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tfReader = TFReader(test_msg_spec, BUFSIZE, buffer)
        self.assertEqual(0, tfReader.position)
        self.assertEqual(BUFSIZE, tfReader.capacity)
        self.assertEqual(BUFSIZE, len(tfReader.buffer))

    def testReaderCreator(self):
        BUFSIZE = 1024
        tfReader = TFReader.create(test_msg_spec, BUFSIZE)
        self.assertTrue(isinstance(tfReader, TFReader))
        self.assertEqual(0, tfReader.position)
        self.assertEqual(BUFSIZE, tfReader.capacity)

    # next two are specific to TFWriter
    def testWriterCtor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tfWriter = TFWriter(test_msg_spec, BUFSIZE, buffer)
        self.assertEqual(0, tfWriter.position)
        self.assertEqual(BUFSIZE, tfWriter.capacity)

    def testWriterCreator(self):
        BUFSIZE = 1024
        tfWriter = TFWriter.create(test_msg_spec, BUFSIZE)
        self.assertTrue(isinstance(tfWriter, TFWriter))
        self.assertEqual(0, tfWriter.position)
        self.assertEqual(BUFSIZE, tfWriter.capacity)

    def doRoundTripField(self, writer, reader, nnn, field_type, value):
        writer.put_next(nnn, value)
#       # DEBUG
#       tfBuf   = writer.buffer
#       print "after put buffer is " ,
#       self.dumpBuffer(tfBuf)
#       # END
        reader.get_next()
        self.assertEqual(nnn, reader.field_nbr)
        # XXX THIS SHOULD WORK:
        # self.assertEqual( fType, reader.fType    )
        self.assertEqual(value, reader.value)
        return nnn + 1

    def testWritingAndReading(self):
        BUFSIZE = 16 * 1024
        tfWriter = TFWriter.create(test_msg_spec, BUFSIZE)
        tfBuf = tfWriter.buffer       # we share the buffer
        tfReader = TFReader(test_msg_spec, BUFSIZE, tfBuf)

        nnn = 0                           # 0-based field number

        # field types encoded as varints (8) ========================
        # These are tested in greater detail in testVarint.py; the
        # tests here are to exercise their use in a heterogeneous
        # buffer

        # fields 0: _V_UINT32
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vuint32', 0x1f)
        self.assertEqual(1, nnn)         # DEBUG XXX

        # fields 1: _V_UINT32
        nnn = self.doRoundTripField(
            tfWriter, tfReader, nnn, 'vuint32', 0x172f3e4d)

        # field 2:  _V_UINT64
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vuint64',
                                    0x12345678abcdef3e)

        # field 3: vsInt32
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vsint32', 192)

        # field 4: vsInt32
        # _V_SINT32 (zig-zag encoded, optimal for small values near zero)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vsint32', -192)

        # field 5: _V_SINT64
        nnn = self.doRoundTripField(
            tfWriter, tfReader, nnn, 'vsint64', -193)  # GEEP

        # field 6: _V_UINT32
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vuint32',
                                    0x172f3e4d)
        # field 7: _V_UINT64
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'vuint64',
                                    0xffffffff172f3e4d)

        # _V_BOOL
        # XXX NOT IMPLEMENTED, NOT TESTED

        # _V_ENUM
        # XXX NOT IMPLEMENTED, NOT TESTED

        # encoded as fixed length 32 bit fields =====================
        # field 8: _F_INT32
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'fInt32',
                                    0x172f3e4d)
        # _F_FLOAT
        # XXX STUB XXX not implemented

        # encoded as fixed length 64 bit fields =====================
        # field 9: _F_INT64
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'fInt64',
                                    0xffffffff172f3e4d)
        # _F_DOUBLE
        # XXX STUB XXX not implemented

        # encoded as varint len followed by byte[len] ===============
        # field 10: _L_STRING
        string = self.rng.next_file_name(16)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'lstring', string)

        # field 11: _L_BYTES
        b_val = bytearray(8 + self.rng.next_int16(16))
        self.rng.next_bytes(b_val)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'lbytes', b_val)

        # _L_MSG
        # XXX STUB XXX not implemented

        # fixed length byte sequences, byte[N} ======================
        # field 12: _F_BYTES16
        self.rng.next_bytes(b128)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'fbytes16', b128)

        # field 13: _F_BYTES20
        self.rng.next_bytes(b160)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'fbytes20', b160)

        # may want to introduce eg fNodeID20 and fSha1Key types
        # field 14: _F_BYTES32
        self.rng.next_bytes(b256)
        nnn = self.doRoundTripField(tfWriter, tfReader, nnn, 'fbytes32', b256)

        # may want to introduce eg fSha3Key type, allowing semantic checks

if __name__ == '__main__':
    unittest.main()
