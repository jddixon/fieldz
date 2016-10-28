#!/usr/bin/env python3

# testLogEntry.py
import time
import unittest

from rnglib import SimpleRNG
import fieldz.typed as T
import fieldz.field_types as F
import fieldz.msg_spec as M
import fieldz.reg as R
# from fieldz.tfbuffer import *

rng = SimpleRNG(time.time())

# -- logEntry msgSpec ---------------------------
protocol = 'org.xlattice.upax'
node_reg = R.NodeReg()
proto_reg = R.ProtoReg(protocol, node_reg)
parent = M.ProtoSpec(protocol, proto_reg)
msg_reg = R.MsgReg(proto_reg)
name = 'logEntry'
enum = M.EnumSpec.create('foo', [('not', 0), ('being', 1), ('used', 2), ])
fields = [
    M.FieldSpec(msg_reg, 'timestamp', F.F_UINT32, M.Q_REQUIRED, 0),
    M.FieldSpec(msg_reg, 'node_id', F.F_BYTES20, M.Q_REQUIRED, 1),
    M.FieldSpec(msg_reg, 'key', F.F_BYTES20, M.Q_REQUIRED, 2),
    M.FieldSpec(msg_reg, 'length', F.V_UINT32, M.Q_REQUIRED, 3),
    M.FieldSpec(msg_reg, 'by_', F.L_STRING, M.Q_REQUIRED, 4),
    M.FieldSpec(msg_reg, 'path', F.L_STRING, M.Q_REQUIRED, 5),
]
leMsgSpec = M.MsgSpec(name, proto_reg, parent)
for file in fields:
    leMsgSpec.addField(file)
upaxProtoSpec = M.ProtoSpec(protocol, proto_reg)
upaxProtoSpec.add_enum(enum)
upaxProtoSpec.add_msg(leMsgSpec)

# -- end logEntry msgSpec -----------------------


class TestLogEntry (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpWireBuffer(self, wb):
        for i in range(16):
            print("0x%02x " % wb.buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def test_proto_spec(self):
        self.assertIsNotNone(node_reg)
        self.assertIsNotNone(proto_reg)

    def testConstructors(self):
        pSpec = upaxProtoSpec
        self.assertEqual(protocol, pSpec.name)
        self.assertEqual(enum, pSpec.enums[0])
        self.assertEqual(leMsgSpec, pSpec.msgs[0])
        self.assertEqual(0, len(pSpec.seqs))

    def testWritingAndReading(self):
        BUFSIZE = 16 * 1024
        writer = TFWriter.create(leMsgSpec, BUFSIZE)
        writer.clear()  # should not be necessary

        buf = writer.buffer
        # reader and writer share same buffer
        reader = TFReader(leMsgSpec, BUFSIZE, buf)

        tstamp = int(time.time())
        node_id = bytearray(20)         # 160 bit
        rng.next_bytes(node_id)  # .... random value
        key = bytearray(20)         # 160 bit
        rng.next_bytes(key)  # .... random value
        length = rng.next_int32()
        by_ = rng.next_file_name(16)
        path = 'path/to/' + rng.next_file_name(16)

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
        self.assertEqual('fuint32', F.as_str(reader.field_type))
        self.assertEqual(tstamp, reader.value)
        self.assertEqual(5, reader.position)

        reader.get_next()
        self.assertEqual(1, reader.field_nbr)
        self.assertEqual('fbytes20', F.as_str(reader.field_type))
        self.assertEqual(node_id, reader.value)
        self.assertEqual(26, reader.position)

        reader.get_next()
        self.assertEqual(2, reader.field_nbr)
        self.assertEqual('fbytes20', F.as_str(reader.field_type))
        self.assertEqual(key, reader.value)
        self.assertEqual(47, reader.position)

        reader.get_next()
        self.assertEqual(3, reader.field_nbr)
        self.assertEqual('vuint32', F.as_str(reader.field_type))
        self.assertEqual(length, reader.value)

        reader.get_next()
        self.assertEqual(4, reader.field_nbr)
        self.assertEqual('lstring', F.as_str(reader.field_type))
        self.assertEqual(by_, reader.value)

        reader.get_next()
        self.assertEqual(5, reader.field_nbr)
        self.assertEqual('lstring', F.as_str(reader.field_type))
        self.assertEqual(path, reader.value)

if __name__ == '__main__':
    unittest.main()
