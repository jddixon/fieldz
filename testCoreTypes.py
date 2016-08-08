#!/usr/bin/env python3

# testCoreTypes.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from fieldz.chan import Channel
from fieldz.raw import *
from fieldz.typed import *
import fieldz.msgSpec as M
import fieldz.coreTypes as C
from fieldz.fieldTypes import FieldTypes as F, FieldStr as FS
import fieldz.reg as R
from fieldz.parser import StringMsgSpecParser

import fieldz.coreTypes         # EXPERIMENT

LOG_ENTRY_MSG_SPEC = u"""
# protocol org.xlattice.zoggery
message logEntry:
 timestamp   fuInt32
 nodeID      fBytes20
 key         fBytes20
 length      vuInt32
 by          lString
 path        lString
"""


class TestCoreTypes (unittest.TestCase):

    def setUp(self):
        #       self.rng = SimpleRNG( time.time() )
        pass

    def tearDown(self):
        pass

    # utility functions #############################################
    def makeRegistries(self, protocol):
        nodeReg = R.NodeReg()
        protoReg = R.ProtoReg(protocol, nodeReg)
        msgReg = R.MsgReg(protoReg)
        return (nodeReg, protoReg, msgReg)

    # actual unit tests #############################################
    def testTheEnum(self):
        cTypes = C.CoreTypes()
        self.assertEqual(5, cTypes.maxNdx)
        self.assertEqual(0, cTypes._ENUM_PAIR_SPEC)
        self.assertEqual(5, cTypes._PROTO_SPEC)

    def roundTripToWireFormat(self, chan, n, cType, val):
        nodeReg, protoReg, msgReg = self.makeRegistries(
            'org.xlattice.fieldz.test.roundTrip')

        # DEBUG
        print("roundTrioWireFormat: n = %d, cType = %d" % (n, cType))
        # END
        chan.clear()                            # I guess :-)

        buf = chan.buffer
        putter = M.cPutFuncs[cType]
        getter = M.cGetFuncs[cType]
        # DEBUG
        print("  PUTTER: %s" % putter)
        print("  GETTER: %s" % getter)
        # END
        lenFunc = M.cLenFuncs[cType]
        pLenFunc = M.cPLenFuncs[cType]
        # comment of unknown value/validity:  # BUT cType must be >18!
        h = fieldHdrLen(n, cType)

        rPos = 0  # read
        expectedPos = pLenFunc(val, n)

        putter(chan, val, 0)  # writing field 0
        chan.flip()
        wPos = chan.limit

        self.assertEqual(expectedPos, wPos)

        (pType, n) = readFieldHdr(chan)
        actualHdrLen = chan.position
        self.assertEqual(LEN_PLUS_TYPE, pType)
        self.assertEqual(0, n)    # field number
        self.assertEqual(h, actualHdrLen)

        # FAILS:
        #   if chan is present
        #     enumPairSpecGetter() takes 1 positional argument but 2 were given
        #retVal = getter(msgReg, chan)
        #   else # chan is absent
        #     fieldSpecGetter() missing 1 required  positional argument: 'chan'
        retVal = getter(msgReg, chan)

        # gets the same error:retVal = M.cGetFuncs[cType](chan)

        rPos = chan.position
        # DEBUG
        print("  ROUND TRIP: val    = %s" % val)
        print("              retVal = %s" % retVal)
        # END
        self.assertEqual(val, retVal)

    def testRoundTrippingCoreTypes(self):
        BUFSIZE = 16 * 1024
        chan = Channel(BUFSIZE)
        cTypes = C.CoreTypes()

        # -----------------------------------------------------------
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        # XXX n=0 is wired into roundTripToWireFormat XXX
        n = 0                           # 0-based field number
        s = M.EnumPairSpec('funnyFarm', 497)
        self.roundTripToWireFormat(chan, n, cTypes._ENUM_PAIR_SPEC, s)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        nodeReg, protoReg, msgReg = self.makeRegistries(protocol)
        n = 0                          # 0-based field number
        pairs = [('funnyFarm', 497),
                 ('myOpia', 53),
                 ('frogHeaven', 919),
                 ]
        s = M.EnumSpec.create('thisEnum', pairs)
        self.assertEqual(3, len(s))
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
#       self.roundTripToWireFormat( chan, n, cTypes._ENUM_SPEC, s)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        nodeReg, protoReg, msgReg = self.makeRegistries(protocol)
        n = 0                          # 0-based field number
        s = M.FieldSpec(msgReg, 'jollyGood', F._V_SINT32, M.Q_OPTIONAL, 37)
        # XXX FAILS: invalid (optionlly dotted) name 'bytearray(b'jollyGood')
        self.roundTripToWireFormat(chan, n, cTypes._FIELD_SPEC, s)

        # -----------------------------------------------------------

        # MsgSpec without enum
        protocol = 'org.xlattice.upax'
        nodeReg, protoReg, msgReg = self.makeRegistries(protocol)
        data = StringIO(LOG_ENTRY_MSG_SPEC)
        p = StringMsgSpecParser(data)
        sOM = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.MsgSpec))

        n = 0
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        self.roundTripToWireFormat(chan, n, cTypes._MSG_SPEC, sOM)


if __name__ == '__main__':
    unittest.main()
