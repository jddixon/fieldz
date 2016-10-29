#!/usr/bin/env python3

# testLogEntry.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.field_types import FieldTypes, FieldStr
import fieldz.typed as T
import fieldz.msg_spec as M
import fieldz.reg as R
# from fieldz.tfbuffer import *

BUFSIZE = 16 * 1024
RNG = SimpleRNG(time.time())

# -- logEntry msgSpec ---------------------------
PROTOCOL = 'org.xlattice.upax'
NODE_REG = R.NodeReg()
PROTO_REG = R.ProtoReg(PROTOCOL, NODE_REG)
PARENT = M.ProtoSpec(PROTOCOL, PROTO_REG)
MSG_REG = R.MsgReg(PROTO_REG)
NAME = 'logEntry'
ENUM = M.EnumSpec.create('foo', [('not', 0), ('being', 1), ('used', 2), ])
FIELDS = [
    M.FieldSpec(MSG_REG, 'timestamp', FieldTypes.F_UINT32, M.Q_REQUIRED, 0),
    M.FieldSpec(MSG_REG, 'node_id', FieldTypes.F_BYTES20, M.Q_REQUIRED, 1),
    M.FieldSpec(MSG_REG, 'key', FieldTypes.F_BYTES20, M.Q_REQUIRED, 2),
    M.FieldSpec(MSG_REG, 'length', FieldTypes.V_UINT32, M.Q_REQUIRED, 3),
    M.FieldSpec(MSG_REG, 'by_', FieldTypes.L_STRING, M.Q_REQUIRED, 4),
    M.FieldSpec(MSG_REG, 'path', FieldTypes.L_STRING, M.Q_REQUIRED, 5),
]
LE_MSG_SPEC = M.MsgSpec(NAME, PROTO_REG, PARENT)
for file in FIELDS:
    LE_MSG_SPEC.addField(file)
UPAX_PROTO_SPEC = M.ProtoSpec(PROTOCOL, PROTO_REG)
UPAX_PROTO_SPEC.add_enum(ENUM)
UPAX_PROTO_SPEC.add_msg(LE_MSG_SPEC)

# -- end logEntry msgSpec -----------------------


class TestLogEntry(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################
    def dump_wire_buffer(self, wb_):
        for i in range(16):
            print("0x%02x " % wb_.buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def test_proto_spec(self):
        self.assertIsNotNone(NODE_REG)
        self.assertIsNotNone(PROTO_REG)

    def test_constructors(self):
        p_spec = UPAX_PROTO_SPEC
        self.assertEqual(PROTOCOL, p_spec.name)
        self.assertEqual(enum, p_spec.enums[0])
        self.assertEqual(LE_MSG_SPEC, p_spec.msgs[0])
        self.assertEqual(0, len(p_spec.seqs))

    def test_writing_and_reading(self):
        writer = TFWriter.create(LE_MSG_SPEC, BUFSIZE)
        writer.clear()  # should not be necessary

        buf = writer.buffer
        # reader and writer share same buffer
        reader = TFReader(LE_MSG_SPEC, BUFSIZE, buf)

        tstamp = int(time.time())
        node_id = bytearray(20)         # 160 bit
        RNG.next_bytes(node_id)  # .... random value
        key = bytearray(20)         # 160 bit
        RNG.next_bytes(key)  # .... random value
        length = RNG.next_int32()
        by_ = RNG.next_file_name(16)
        path = 'path/to/' + RNG.next_file_name(16)

        nnn = 0                           # 0-based field number
        # write a log entry into the buffer
        writer.put_next(nnn, tstamp)
        nnn = nnn + 1
        writer.put_next(nnn, node_id)
        nnn = nnn + 1
        writer.put_next(nnn, key)
        nnn = nnn + 1
        writer.put_next(nnn, length)
        nnn = nnn + 1
        writer.put_next(nnn, by_)
        nnn = nnn + 1
        writer.put_next(nnn, path)

        # now read the buffer to see what actually was written
        self.assertEqual(0, reader.position)

        reader.get_next()
        self.assertEqual(0, reader.field_nbr)
        self.assertEqual('fuint32', FieldStr.as_str(reader.field_type))
        self.assertEqual(tstamp, reader.value)
        self.assertEqual(5, reader.position)

        reader.get_next()
        self.assertEqual(1, reader.field_nbr)
        self.assertEqual('fbytes20', FieldStr.as_str(reader.field_type))
        self.assertEqual(node_id, reader.value)
        self.assertEqual(26, reader.position)

        reader.get_next()
        self.assertEqual(2, reader.field_nbr)
        self.assertEqual('fbytes20', FieldStr.as_str(reader.field_type))
        self.assertEqual(key, reader.value)
        self.assertEqual(47, reader.position)

        reader.get_next()
        self.assertEqual(3, reader.field_nbr)
        self.assertEqual('vuint32', FieldStr.as_str(reader.field_type))
        self.assertEqual(length, reader.value)

        reader.get_next()
        self.assertEqual(4, reader.field_nbr)
        self.assertEqual('lstring', FieldStr.as_str(reader.field_type))
        self.assertEqual(by_, reader.value)

        reader.get_next()
        self.assertEqual(5, reader.field_nbr)
        self.assertEqual('lstring', FieldStr.as_str(reader.field_type))
        self.assertEqual(path, reader.value)

if __name__ == '__main__':
    unittest.main()
