#!/usr/bin/env python3

# testTFWriter.py
import time
import unittest

from rnglib import SimpleRNG

from wireops.enum import FieldTypes

from fieldz import reg
from fieldz.enum import Quants
from fieldz.msg_spec import FieldSpec, MsgSpec, ProtoSpec
from fieldz.tfbuffer import TFBuffer, TFReader, TFWriter

# scratch variables
B128 = bytearray(16)
B160 = bytearray(20)
B256 = bytearray(32)

# msgSpec -----------------------------------------------------------
PROTOCOL = 'org.xlattice.upax'
NAME = 'TEST_MSG_SPEC'
NODE_REG = reg.NodeReg()
PROTO_REG = reg.ProtoReg(PROTOCOL, NODE_REG)
MSG_REG = reg.MsgReg(PROTO_REG)
PARENT = ProtoSpec(PROTOCOL, PROTO_REG)

# no enum is used

# XXX MISSING reg; BUT DO WE REALLY WANT FIELD NAMES IN THE REGISTRY?

FIELDS = [

    # pylint: disable=no-member
    FieldSpec(MSG_REG, 'i32', FieldTypes.V_UINT32, Quants.REQUIRED, 0),
    FieldSpec(
        MSG_REG,
        'i32bis',
        FieldTypes.V_UINT32,
        Quants.REQUIRED,
        1),
    FieldSpec(MSG_REG, 'i64', FieldTypes.V_UINT64, Quants.REQUIRED, 2),
    FieldSpec(MSG_REG, 'si32', FieldTypes.V_SINT32, Quants.REQUIRED, 3),
    FieldSpec(
        MSG_REG,
        'si32bis',
        FieldTypes.V_SINT32,
        Quants.REQUIRED,
        4),
    FieldSpec(MSG_REG, 'si64', FieldTypes.V_SINT64, Quants.REQUIRED, 5),
    FieldSpec(
        MSG_REG,
        'vuint32',
        FieldTypes.V_UINT32,
        Quants.REQUIRED,
        6),
    FieldSpec(
        MSG_REG,
        'vuint64',
        FieldTypes.V_UINT64,
        Quants.REQUIRED,
        7),
    # take care with gaps from here
    FieldSpec(
        MSG_REG,
        'fint32',
        FieldTypes.V_UINT32,
        Quants.REQUIRED,
        8),
    FieldSpec(
        MSG_REG,
        'fint64',
        FieldTypes.V_UINT64,
        Quants.REQUIRED,
        9),
    FieldSpec(MSG_REG, 'lstr', FieldTypes.L_STRING, Quants.REQUIRED, 10),
    FieldSpec(
        MSG_REG,
        'lbytes',
        FieldTypes.L_BYTES,
        Quants.REQUIRED,
        11),
    FieldSpec(
        MSG_REG,
        'lbytes16',
        FieldTypes.F_BYTES16,
        Quants.REQUIRED,
        12),
    FieldSpec(
        MSG_REG,
        'lbytes20',
        FieldTypes.F_BYTES20,
        Quants.REQUIRED,
        13),
    FieldSpec(
        MSG_REG,
        'lbytes32',
        FieldTypes.F_BYTES32,
        Quants.REQUIRED,
        14),
]

TEST_MSG_SPEC = MsgSpec(NAME, PROTO_REG, PARENT)
for field in FIELDS:
    TEST_MSG_SPEC.add_field(field)

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

    def do_round_trip_field(self, writer, reader, fnbr, field_type, value):

        #############################################################
        # THIS IS WRONG: header is determined by fnbr and field_type, then
        # this is followed by value.
        #############################################################

        writer.put_next(fnbr, value)                                 # LINE 178
        # DEBUG
        tf_buf = writer.buffer
        print("after put buffer is ", end='')
        self.dump_buffer(tf_buf)
        # END
        reader.get_next()
        self.assertEqual(fnbr, reader.field_nbr)
        # field_type should be an enum member
        # DEBUG
        print("field_type is a ", type(field_type))
        print("reader.field_type is a ", type(reader.field_type))

        # END
        self.assertEqual(field_type, reader.field_type)
        self.assertEqual(value, reader.value)
        return fnbr + 1

    def test_writing_and_reading(self):
        BUFSIZE = 16 * 1024
        tf_writer = TFWriter.create(TEST_MSG_SPEC, BUFSIZE)
        tf_buf = tf_writer.buffer       # we share the buffer
        tf_reader = TFReader(TEST_MSG_SPEC, BUFSIZE, tf_buf)

        fnbr = 0                           # 0-based field number

        # field types encoded as varints (8) ========================
        # These are tested in greater detail in wireops/test_varint.py;
        # the tests here are to exercise their use in a heterogeneous
        # buffer

        # pylint: disable=no-member
        # field 0: _V_UINT32
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_UINT32, 0x1f)                      # LINE 212
        self.assertEqual(1, fnbr)                           # DEBUG XXX

        # field 1: _V_UINT32
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_UINT32, 0x172f3e4d)

        # field 2:  _V_UINT64
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_UINT64, 0x12345678abcdef3e)

        # field 3: vsInt32
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_SINT32, 192)

        # field 4: vsInt32
        # _V_SINT32 (zig-zag encoded, optimal for small values near zero)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_SINT32, -192)

        # field 5: _V_SINT64
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_SINT64, -193)  # GEEP

        # field 6: _V_UINT32
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_UINT32, 0x172f3e4d)

        # field 7: _V_UINT64
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.V_UINT64, 0xffffffff172f3e4d)

        # _V_BOOL
        # XXX NOT IMPLEMENTED, NOT TESTED

        # _V_ENUM
        # XXX NOT IMPLEMENTED, NOT TESTED

        # encoded as fixed length 32 bit fields =====================
        # field 8: _F_INT32
        # fnbr = self.do_round_trip_field(
        #    tf_writer, tf_reader, fnbr,
        #    FieldTypes.F_INT32, 0x172f3e4d)

        # _F_FLOAT
        # XXX STUB XXX not implemented

        # encoded as fixed length 64 bit fields =====================
        # field 9: _F_INT64
        # fnbr = self.do_round_trip_field(
        #    tf_writer, tf_reader, fnbr,
        #    FieldTypes.F_INT64, 0xffffffff172f3e4d)

        # _F_DOUBLE
        # XXX STUB XXX not implemented

        # DEBUG #######################
        return
        # END #########################

        # encoded as varint len followed by byte[len] ===============
        # field 10: _L_STRING
        string = self.rng.next_file_name(16)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.L_STRING, string)

        # field 11: _L_BYTES
        b_val = bytearray(8 + self.rng.next_int16(16))
        self.rng.next_bytes(b_val)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.L_BYTES, b_val)

        # _L_MSG
        # XXX STUB XXX not implemented

        # fixed length byte sequences, byte[N} ======================
        # field 12: _F_BYTES16
        self.rng.next_bytes(B128)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.F_BYTES16, B128)

        # field 13: _F_BYTES20
        self.rng.next_bytes(B160)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.F_BYTES20, B160)

        # may want to introduce eg fNodeID20 and fSha1Key types
        # field 14: _F_BYTES32
        self.rng.next_bytes(B256)
        fnbr = self.do_round_trip_field(
            tf_writer, tf_reader, fnbr,
            FieldTypes.F_BYTES32, B256)

        # may want to introduce eg fSha3Key type, allowing semantic checks

if __name__ == '__main__':
    unittest.main()
