#!/usr/bin/env python3
# testCoreTypes.py

import unittest
from io import StringIO

from wireops.chan import Channel
from wireops.raw import(
    LEN_PLUS_TYPE,
    field_hdr_len,
    read_field_hdr,
)
import fieldz.msg_spec as M
from fieldz.core_types import CoreTypes
from fieldz.reg import NodeReg, ProtoReg, MsgReg
from fieldz.parser import StringMsgSpecParser
from wireops.field_types import FieldTypes

LOG_ENTRY_MSG_SPEC = u"""
# protocol org.xlattice.zoggery
message logEntry:
 timestamp   fuint32
 nodeID      fbytes20
 key         fbytes20
 length      vuint32
 by          lstring
 path        lstring
"""


class TestCoreTypes(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_registries(self, protocol):
        node_reg = NodeReg()
        proto_reg = ProtoReg(protocol, node_reg)
        msg_reg = MsgReg(proto_reg)
        return (node_reg, proto_reg, msg_reg)

    # actual unit tests #############################################
    def test_the_enum(self):
        c_types = CoreTypes()
        self.assertEqual(c_types.ENUM_PAIR_SPEC, 0)
        self.assertEqual(c_types.ENUM_SPEC, 1)
        self.assertEqual(c_types.FIELD_SPEC, 2)
        self.assertEqual(c_types.MSG_SPEC, 3)
        self.assertEqual(c_types.SEQ_SPEC, 4)
        self.assertEqual(c_types.PROTO_SPEC, 5)
        self.assertEqual(c_types.max_ndx, 5)

    def round_trip_to_wire_format(self, chan, nnn, c_type, val):
        node_reg, proto_reg, msg_reg = self.make_registries(
            'org.xlattice.fieldz.test.roundTrip')

        # DEBUG
        print("roundTrioWireFormat: n = %d, c_type = %d" % (nnn, c_type))
        # END
        chan.clear()                            # I guess :-)

        buf = chan.buffer
        putter = M.C_PUT_FUNCS[c_type]
        getter = M.C_GET_FUNCS[c_type]
        # DEBUG
        print("  PUTTER: %s" % putter)
        print("  GETTER: %s" % getter)
        # END
        len_func = M.C_LEN_FUNCS[c_type]
        p_len_func = M.C_P_LEN_FUNCS[c_type]
        # comment of unknown value/validity:  # BUT c_type must be >18!
        len_ = field_hdr_len(nnn, c_type)

        r_pos = 0  # read
        expected_pos = p_len_func(val, nnn)

        putter(chan, val, 0)  # writing field 0
        chan.flip()
        w_pos = chan.limit

        (p_type, nnn) = read_field_hdr(chan)
        actual_hdr_len = chan.position
        self.assertEqual(LEN_PLUS_TYPE, p_type)
        self.assertEqual(0, nnn)    # field number
        self.assertEqual(len_, actual_hdr_len)

        # FAILS:
        #   if chan is present
        #     enumPairSpecGetter() takes 1 positional argument but 2 were given
        #ret_val = getter(msgReg, chan)
        #   else # chan is absent
        #     fieldSpecGetter() missing 1 required  positional argument: 'chan'
        # 2016-10-30 GOT FIRST FAILURE MODE
        ret_val = getter(msg_reg, chan)

        # gets the same error:ret_val = M.cGetFuncs[c_type](chan)

        r_pos = chan.position
        # DEBUG
        print("  ROUND TRIP: val     = %s" % val)
        print("              ret_val = %s" % ret_val)
        # END
        self.assertEqual(val, ret_val)

    def test_round_tripping_core_types(self):
        buf_size = 16 * 1024
        chan = Channel(buf_size)
        c_types = CoreTypes()

        # -----------------------------------------------------------
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        # XXX n=0 is wired into round_trip_to_wire_format XXX
        nnn = 0                           # 0-based field number
        string = M.EnumPairSpec('funnyFarm', 497)
        self.round_trip_to_wire_format(
            chan, nnn, c_types.ENUM_PAIR_SPEC, string)

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
        self.round_trip_to_wire_format(chan, nnn, c_types.ENUM_SPEC, string)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        nnn = 0                          # 0-based field number
        string = M.FieldSpec(
            msg_reg,
            'jollyGood',
            FieldTypes.V_SINT32,
            M.Q_OPTIONAL,
            37)
        self.round_trip_to_wire_format(chan, nnn, c_types.FIELD_SPEC, string)

        # -----------------------------------------------------------

        # MsgSpec without enum
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        data = StringIO(LOG_ENTRY_MSG_SPEC)
        ppp = StringMsgSpecParser(data)

        str_obj_model = ppp.parse()    # object model from string serialization

        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.MsgSpec))

        nnn = 0

        # XXX FAILS:
        self.round_trip_to_wire_format(
            chan, nnn, c_types.MSG_SPEC, str_obj_model)

if __name__ == '__main__':
    unittest.main()
