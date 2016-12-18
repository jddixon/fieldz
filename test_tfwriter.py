#!/usr/bin/env python3

# testTFWriter.py
import time
import unittest

from rnglib import SimpleRNG

import fieldz.reg as R

from fieldz.msg_spec import(FieldSpec, MsgSpec, ProtoSpec,
                            Q_REQUIRED)  # , Q_OPTIONAL, Q_PLUS, Q_STAR)
from fieldz.tfbuffer import TFBuffer, TFReader, TFWriter
from wireops.field_types import FieldStr

# scratch variables
B128 = bytearray(16)
B160 = bytearray(20)
B256 = bytearray(32)

# msgSpec -----------------------------------------------------------
PROTOCOL = 'org.xlattice.upax'
NAME = 'TEST_MSG_SPEC'
NODE_REG = R.NodeReg()
PROTO_REG = R.ProtoReg(PROTOCOL, NODE_REG)
MSG_REG = R.MsgReg(PROTO_REG)
PARENT = ProtoSpec(PROTOCOL, PROTO_REG)

# no enum is used

# XXX MISSING reg; BUT DO WE REALLY WANT FIELD NAMES IN THE REGISTRY?

NDX = FieldStr().ndx

FIELDS = [

    FieldSpec(MSG_REG, 'i32', NDX('vuint32'), Q_REQUIRED, 0),
    FieldSpec(MSG_REG, 'i32bis', NDX('vuint32'), Q_REQUIRED, 1),
    FieldSpec(MSG_REG, 'i64', NDX('vuint64'), Q_REQUIRED, 2),
    FieldSpec(MSG_REG, 'si32', NDX('vsint32'), Q_REQUIRED, 3),
    FieldSpec(MSG_REG, 'si32bis', NDX('vsint32'), Q_REQUIRED, 4),
    FieldSpec(MSG_REG, 'si64', NDX('vsint64'), Q_REQUIRED, 5),
    FieldSpec(MSG_REG, 'vuint32', NDX('vuint32'), Q_REQUIRED, 6),
    FieldSpec(MSG_REG, 'vuint64', NDX('vuint64'), Q_REQUIRED, 7),
    # take care with gaps from here
    FieldSpec(MSG_REG, 'fint32', NDX('vuint32'), Q_REQUIRED, 8),
    FieldSpec(MSG_REG, 'fint64', NDX('vuint64'), Q_REQUIRED, 9),
    FieldSpec(MSG_REG, 'lstr', NDX('lstring'), Q_REQUIRED, 10),
    FieldSpec(MSG_REG, 'lbytes', NDX('lbytes'), Q_REQUIRED, 11),
    FieldSpec(MSG_REG, 'lbytes16', NDX('fbytes16'), Q_REQUIRED, 12),
    FieldSpec(MSG_REG, 'lbytes20', NDX('fbytes20'), Q_REQUIRED, 13),
    FieldSpec(MSG_REG, 'lbytes32', NDX('fbytes32'), Q_REQUIRED, 14),
]
# XXX contains no fields
TEST_MSG_SPEC = MsgSpec(NAME, PROTO_REG, PARENT)

BUFSIZE = 1024


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
    def test_buffer_ctor(self):
        buffer = [0] * BUFSIZE
        tf_buf = TFBuffer(TEST_MSG_SPEC, BUFSIZE, buffer)
        self.assertEqual(0, tf_buf.position)
        self.assertEqual(BUFSIZE, tf_buf.capacity)

    def test_buffer_creator(self):
        BUFSIZE = 1024
        tf_buf = TFBuffer.create(TEST_MSG_SPEC, BUFSIZE)
        self.assertTrue(isinstance(tf_buf, TFBuffer))
        self.assertEqual(0, tf_buf.position)
        self.assertEqual(BUFSIZE, tf_buf.capacity)

    # and these two methods are all that's left of testTFReader.py
    def test_reader_ctor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tf_reader = TFReader(TEST_MSG_SPEC, BUFSIZE, buffer)
        self.assertEqual(0, tf_reader.position)
        self.assertEqual(BUFSIZE, tf_reader.capacity)
        self.assertEqual(BUFSIZE, len(tf_reader.buffer))

    def test_reader_creator(self):
        BUFSIZE = 1024
        tf_reader = TFReader.create(TEST_MSG_SPEC, BUFSIZE)
        self.assertTrue(isinstance(tf_reader, TFReader))
        self.assertEqual(0, tf_reader.position)
        self.assertEqual(BUFSIZE, tf_reader.capacity)

    # next two are specific to TFWriter
    def test_writer_ctor(self):
        BUFSIZE = 1024
        buffer = bytearray(BUFSIZE)
        tf_writer = TFWriter(TEST_MSG_SPEC, BUFSIZE, buffer)
        self.assertEqual(0, tf_writer.position)
        self.assertEqual(BUFSIZE, tf_writer.capacity)

    def test_writer_creator(self):
        BUFSIZE = 1024
        tf_writer = TFWriter.create(TEST_MSG_SPEC, BUFSIZE)
        self.assertTrue(isinstance(tf_writer, TFWriter))
        self.assertEqual(0, tf_writer.position)
        self.assertEqual(BUFSIZE, tf_writer.capacity)

    def do_round_trip_field(self, writer, reader, idx, field_type, value):
        writer.put_next(idx, value)
#       # DEBUG
#       tfBuf   = writer.buffer
#       print "after put buffer is " ,
#       self.dumpBuffer(tfBuf)
#       # END
        reader.get_next()
        self.assertEqual(idx, reader.field_nbr)
        # XXX THIS SHOULD WORK:
        # self.assertEqual( fType, reader.fType    )
        self.assertEqual(value, reader.value)
        return idx + 1

    def test_writing_and_reading(self):
        BUFSIZE = 16 * 1024
        tf_writer = TFWriter.create(TEST_MSG_SPEC, BUFSIZE)
        tf_buf = tf_writer.buffer       # we share the buffer
        tf_reader = TFReader(TEST_MSG_SPEC, BUFSIZE, tf_buf)

        idx = 0                           # 0-based field number

        # field types encoded as varints (8) ========================
        # These are tested in greater detail in testVarint.py; the
        # tests here are to exercise their use in a heterogeneous
        # buffer

        # field 0: _V_UINT32
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vuint32', 0x1f)
        self.assertEqual(1, idx)         # DEBUG XXX

        # field 1: _V_UINT32
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vuint32', 0x172f3e4d)

        # field 2:  _V_UINT64
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vuint64', 0x12345678abcdef3e)

        # field 3: vsInt32
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vsint32', 192)

        # field 4: vsInt32
        # _V_SINT32 (zig-zag encoded, optimal for small values near zero)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vsint32', -192)

        # field 5: _V_SINT64
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vsint64', -193)  # GEEP

        # field 6: _V_UINT32
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vuint32', 0x172f3e4d)
        # field 7: _V_UINT64
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'vuint64', 0xffffffff172f3e4d)

        # _V_BOOL
        # XXX NOT IMPLEMENTED, NOT TESTED

        # _V_ENUM
        # XXX NOT IMPLEMENTED, NOT TESTED

        # encoded as fixed length 32 bit fields =====================
        # field 8: _F_INT32
        idx = self.do_round_trip_field(tf_writer, tf_reader, idx, 'fint32',
                                       0x172f3e4d)
        # _F_FLOAT
        # XXX STUB XXX not implemented

        # encoded as fixed length 64 bit fields =====================
        # field 9: _F_INT64
        idx = self.do_round_trip_field(tf_writer, tf_reader, idx, 'fint64',
                                       0xffffffff172f3e4d)
        # _F_DOUBLE
        # XXX STUB XXX not implemented

        # encoded as varint len followed by byte[len] ===============
        # field 10: _L_STRING
        string = self.rng.next_file_NAME(16)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'lstring', string)

        # field 11: _L_BYTES
        b_val = bytearray(8 + self.rng.next_int16(16))
        self.rng.next_bytes(b_val)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'lbytes', b_val)

        # _L_MSG
        # XXX STUB XXX not implemented

        # fixed length byte sequences, byte[N} ======================
        # field 12: _F_BYTES16
        self.rng.next_bytes(B128)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'fbytes16', B128)

        # field 13: _F_BYTES20
        self.rng.next_bytes(B160)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'fbytes20', B160)

        # may want to introduce eg fNodeID20 and fSha1Key types
        # field 14: _F_BYTES32
        self.rng.next_bytes(B256)
        idx = self.do_round_trip_field(
            tf_writer, tf_reader, idx, 'fbytes32', B256)

        # may want to introduce eg fSha3Key type, allowing semantic checks

if __name__ == '__main__':
    unittest.main()
