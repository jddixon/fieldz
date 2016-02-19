#!/usr/bin/python3

# testLogEntry.py
import time, unittest

from rnglib         import SimpleRNG
import fieldz.typed         as T
import fieldz.fieldTypes    as F
import fieldz.msgSpec       as M
import fieldz.reg           as R
from fieldz.tfbuffer    import *

rng = SimpleRNG( time.time() )

# -- logEntry msgSpec ---------------------------
protocol= 'org.xlattice.upax'
nodeReg = R.NodeReg()
protoReg= R.ProtoReg(protocol, nodeReg)
msgReg  = R.MsgReg(protoReg)
name    = 'logEntry'
enum    = M.EnumSpec.create('foo', [('not',0), ('being',1), ('used',2),])
fields  = [ \
        M.FieldSpec(msgReg, 'timestamp', F._F_UINT32,   M.Q_REQUIRED, 0),
        M.FieldSpec(msgReg, 'nodeID',    F._F_BYTES20,  M.Q_REQUIRED, 1),
        M.FieldSpec(msgReg, 'key',       F._F_BYTES20,  M.Q_REQUIRED, 2),
        M.FieldSpec(msgReg, 'length',    F._V_UINT32,   M.Q_REQUIRED, 3),
        M.FieldSpec(msgReg, 'by',        F._L_STRING,   M.Q_REQUIRED, 4),
        M.FieldSpec(msgReg, 'path',      F._L_STRING,   M.Q_REQUIRED, 5),
]
leMsgSpec       = M.MsgSpec(name, protoReg, msgReg)
for f in fields:
    leMsgSpec.addField(f)
upaxProtoSpec   = M.ProtoSpec(protocol, protoReg)
upaxProtoSpec.addEnum(enum)
upaxProtoSpec.addMsg(leMsgSpec)

# -- end logEntry msgSpec -----------------------

class TestLogEntry (unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpWireBuffer (self, wb):
        for i in range(16):
            print("0x%02x " % wb.buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def testProtoSpec(self):
        self.assertIsNotNone(nodeReg)
        self.assertIsNotNone(protoReg)

    def testConstructors(self):
        pSpec = upaxProtoSpec
        self.assertEqual(protocol,     pSpec.name)
        self.assertEqual(enum,         pSpec.enums[0])
        self.assertEqual(leMsgSpec,    pSpec.msgs[0])
        self.assertEqual(0,            len(pSpec.seqs))

    def testWritingAndReading(self):
        BUFSIZE = 16*1024
        writer  = TFWriter.create(leMsgSpec, BUFSIZE)
        writer.clear()  # should not be necessary

        buf     = writer.buffer
        reader  = TFReader(leMsgSpec, BUFSIZE, buf) # reader and writer share same buffer

        t       = int(time.time())
        nodeID  = bytearray(20)         # 160 bit
        rng.nextBytes(nodeID)           #        .... random value
        key     = bytearray(20)         # 160 bit
        rng.nextBytes(key)              #        .... random value
        length  = rng.nextInt32()
        by      = rng.nextFileName(16)
        path    = 'path/to/' + rng.nextFileName(16)

        n = 0                           # 0-based field number
        # write a log entry into the buffer
        writer.putNext(n, t);           n = n + 1
        writer.putNext(n, nodeID);      n = n + 1
        writer.putNext(n, key);         n = n + 1
        writer.putNext(n, length);      n = n + 1
        writer.putNext(n, by);          n = n + 1
        writer.putNext(n, path)

        # now read the buffer to see what actually was written
        self.assertEqual(0,            reader.position)

        reader.getNext()
        self.assertEqual(0,            reader.fieldNbr)
        self.assertEqual('fuInt32',    F.asStr(reader.fType))
        self.assertEqual(t,            reader.value) 
        self.assertEqual(5,            reader.position)

        reader.getNext()
        self.assertEqual(1,            reader.fieldNbr)
        self.assertEqual('fBytes20',   F.asStr(reader.fType))
        self.assertEqual(nodeID,       reader.value)
        self.assertEqual(26,           reader.position)

        reader.getNext()
        self.assertEqual(2,            reader.fieldNbr)
        self.assertEqual('fBytes20',   F.asStr(reader.fType))
        self.assertEqual(key,          reader.value)
        self.assertEqual(47,           reader.position)

        reader.getNext()
        self.assertEqual(3,            reader.fieldNbr)
        self.assertEqual('vuInt32',    F.asStr(reader.fType))
        self.assertEqual(length,       reader.value)

        reader.getNext()
        self.assertEqual(4,            reader.fieldNbr)
        self.assertEqual('lString',    F.asStr(reader.fType))
        self.assertEqual(by,           reader.value)

        reader.getNext()
        self.assertEqual(5,            reader.fieldNbr)
        self.assertEqual('lString',    F.asStr(reader.fType))
        self.assertEqual(path,         reader.value)

if __name__ == '__main__':
    unittest.main()
