#!/usr/bin/env python3

# testCoreTypes.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from fieldz.chan import Channel
# from fieldz.raw import *
# from fieldz.typed import *
import fieldz.msg_spec as M
import fieldz.core_types as C
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.reg as R
from fieldz.parser import StringMsgSpecParser

import fieldz.core_types         # EXPERIMENT

LOG_ENTRYMSG_SPEC = u"""
# protocol org.xlattice.zoggery
message logEntry:
 timestamp   fuInt32
 nodeID      fBytes20
 key         fBytes20
 length      vuInt32
 by          lString
 path        lString
"""


class TestCoreTypes(unittest.TestCase):

    def setUp(self):
        #       self.rng = SimpleRNG( time.time() )
        pass

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_registries(self, protocol):
        node_reg = R.NodeReg()
        proto_reg = R.ProtoReg(protocol, node_reg)
        msg_reg = R.MsgReg(proto_reg)
        return (node_reg, proto_reg, msg_reg)

    # actual unit tests #############################################
    def testTheEnum(self):
        C_TYPES = C.CoreTypes()
        self.assertEqual(5, C_TYPES.max_ndx)
        self.assertEqual(0, C_TYPES.ENUM_PAIR_SPEC)
        self.assertEqual(5, C_TYPES.PROTO_SPEC)

    def roundTripToWireFormat(self, chan, nnn, cType, val):
        node_reg, proto_reg, msg_reg = self.make_registries(
            'org.xlattice.fieldz.test.roundTrip')

        # DEBUG
        print("roundTrioWireFormat: n = %d, cType = %d" % (nnn, cType))
        # END
        chan.clear()                            # I guess :-)

        buf = chan.buffer
        putter = M.C_PUT_FUNCS[cType]
        getter = M.C_GET_FUNCS[cType]
        # DEBUG
        print("  PUTTER: %s" % putter)
        print("  GETTER: %s" % getter)
        # END
        len_func = M.C_LEN_FUNCS[cType]
        p_len_func = M.C_P_LEN_FUNCS[cType]
        # comment of unknown value/validity:  # BUT cType must be >18!
        h = field_hdr_len(nnn, cType)

        rPos = 0  # read
        expectedPos = p_len_func(val, nnn)

        putter(chan, val, 0)  # writing field 0
        chan.flip()
        wPos = chan.limit

        self.assertEqual(expectedPos, wPos)

        (p_type, nnn) = read_field_hdr(chan)
        actualHdrLen = chan.position
        self.assertEqual(LEN_PLUS_TYPE, p_type)
        self.assertEqual(0, nnn)    # field number
        self.assertEqual(h, actualHdrLen)

        # FAILS:
        #   if chan is present
        #     enumPairSpecGetter() takes 1 positional argument but 2 were given
        #retVal = getter(msgReg, chan)
        #   else # chan is absent
        #     fieldSpecGetter() missing 1 required  positional argument: 'chan'
        retVal = getter(msg_reg, chan)

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
        C_TYPES = C.CoreTypes()

        # -----------------------------------------------------------
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        # XXX n=0 is wired into roundTripToWireFormat XXX
        nnn = 0                           # 0-based field number
        string = M.EnumPairSpec('funnyFarm', 497)
        self.roundTripToWireFormat(chan, nnn, C_TYPES.ENUM_PAIR_SPEC, string)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        nnn = 0                          # 0-based field number
        pairs = [('funnyFarm', 497),
                 ('myOpia', 53),
                 ('frogHeaven', 919),
                 ]
        string = M.EnumSpec.create('thisEnum', pairs)
        self.assertEqual(3, len(string))
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
#       self.roundTripToWireFormat( chan, n, cTypes.ENUM_SPEC, s)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        nnn = 0                          # 0-based field number
        string = M.FieldSpec(
            msg_reg,
            'jollyGood',
            F.V_SINT32,
            M.Q_OPTIONAL,
            37)
        # XXX FAILS: invalid (optionlly dotted) name 'bytearray(b'jollyGood')
        self.roundTripToWireFormat(chan, nnn, C_TYPES.FIELD_SPEC, string)

        # -----------------------------------------------------------

        # MsgSpec without enum
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        data = StringIO(LOG_ENTRYMSG_SPEC)
        ppp = StringMsgSpecParser(data)
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.MsgSpec))

        nnn = 0
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        self.roundTripToWireFormat(chan, nnn, C_TYPES.MSG_SPEC, str_obj_model)


if __name__ == '__main__':
    unittest.main()
