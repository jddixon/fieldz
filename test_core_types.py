#!/usr/bin/env python3
# testCoreTypes.py

import unittest
from io import StringIO

from wireops.chan import Channel
from wireops.enum import PrimTypes
from wireops.raw import(
    field_hdr_len,
    read_field_hdr,
)
import fieldz.msg_spec as M
from fieldz.enum import CoreTypes
from fieldz.reg import NodeReg, ProtoReg, MsgReg
from fieldz.parser import StringMsgSpecParser
from wireops.field_types import FieldTypes

LOG_ENTRY_MSG_SPEC = """
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

    def test_new_coretypes_enum(self):
        """
        Test CoreTypes as redefined 2017-01-30.

        CoreTypes is now an IntEnum with sym() and from_sym() methods.
        """
        for ndx, _ in enumerate(CoreTypes):
            self.assertEqual(_.value, ndx)
            self.assertEqual(CoreTypes.from_sym(_.sym), _)
        self.assertEqual(len(CoreTypes), CoreTypes.PROTO_SPEC + 1)

    # utility functions #############################################
    def make_registries(self, protocol):
        node_reg = NodeReg()
        proto_reg = ProtoReg(protocol, node_reg)
        msg_reg = MsgReg(proto_reg)
        return (node_reg, proto_reg, msg_reg)

    # actual unit tests #############################################
    def test_the_enum(self):
        self.assertEqual(CoreTypes.ENUM_PAIR_SPEC.sym, 'EnumPairSpec')
        self.assertEqual(CoreTypes.ENUM_SPEC.sym, 'EnumSpec')
        self.assertEqual(CoreTypes.FIELD_SPEC.sym, 'FieldSpec')
        self.assertEqual(CoreTypes.MSG_SPEC.sym, 'MsgSpec')
        self.assertEqual(CoreTypes.SEQ_SPEC.sym, 'SeqSpec')
        self.assertEqual(CoreTypes.PROTO_SPEC.sym, 'ProtoSpec')
        self.assertEqual(len(CoreTypes), 6)

    def round_trip_to_wire_format(self, chan, field_nbr, c_type, val):
        node_reg, proto_reg, msg_reg = self.make_registries(
            'org.xlattice.fieldz.test.roundTrip')

        # DEBUG
        print("roundTrioWireFormat: n = %d, c_type = %d (%s)" % (
            field_nbr, c_type.value, c_type.sym))
        print("  val is a ", type(val))
        print("     symbol '%s' value '%s'" % (val.symbol, val.value))
        # END    ********************** <--- !!!
        chan.clear()                            # I guess :-)

        buf = chan.buffer
        putter = M.C_PUT_FUNCS[c_type.value]
        getter = M.C_GET_FUNCS[c_type.value]
        len_func = M.C_LEN_FUNCS[c_type.value]
        p_len_func = M.C_P_LEN_FUNCS[c_type.value]
        # comment of unknown value/validity:  # BUT c_type.value must be >18!

        # XXX THIS IS SIMPLY WRONG: field_hdr_len expects a FieldType
        len_ = field_hdr_len(field_nbr, c_type)

        r_pos = 0  # read
        expected_pos = p_len_func(val, field_nbr)

        putter(chan, val, 0)  # writing field 0
        chan.flip()
        w_pos = chan.limit

        (p_type, field_nbr) = read_field_hdr(chan)
        actual_hdr_len = chan.position
        self.assertEqual(PrimTypes.LEN_PLUS, p_type)
        self.assertEqual(0, field_nbr)    # field number
        self.assertEqual(len_, actual_hdr_len)

        # FAILS:
        #   if chan is present
        #     enumPairSpecGetter() takes 1 positional argument but 2 were given
        #ret_val = getter(msgReg, chan)
        #   else # chan is absent
        #     field_spec_getter() missing 1 required positional argument: 'chan'
        # 2016-10-30 GOT FIRST FAILURE MODE
        ret_val = getter(msg_reg, chan)

        # gets the same error:ret_val = M.cGetFuncs[c_type.value](chan)

        r_pos = chan.position
        # DEBUG
        print("  ROUND TRIP: val     = %s" % val)
        print("              ret_val = %s" % ret_val)
        # END
        self.assertEqual(val, ret_val)

    def test_round_tripping_core_types(self):
        buf_size = 16 * 1024
        chan = Channel(buf_size)

        # -----------------------------------------------------------
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        # XXX n=0 is wired into round_trip_to_wire_format XXX
        field_nbr = 0                           # 0-based field number
        ser = M.EnumPairSpec('funnyFarm', 497)
        self.round_trip_to_wire_format(
            chan, field_nbr, CoreTypes.ENUM_PAIR_SPEC, ser)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        field_nbr = 0                          # 0-based field number
        pairs = [('funnyFarm', 497),
                 ('myOpia', 53),
                 ('frogHeaven', 919),
                 ]
        ser = M.EnumSpec.create('thisEnum', pairs)
        self.assertEqual(3, len(ser))
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        self.round_trip_to_wire_format(
            chan, field_nbr, CoreTypes.ENUM_SPEC, ser)

        # -----------------------------------------------------------
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        field_nbr = 0                          # 0-based field number
        ser = M.FieldSpec(
            msg_reg,
            'jollyGood',
            FieldTypes.V_SINT32,
            Quants.OPTIONAL,
            37)
        self.round_trip_to_wire_format(
            chan, field_nbr, CoreTypes.FIELD_SPEC, ser)

        # -----------------------------------------------------------

        # MsgSpec without enum
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        data = StringIO(LOG_ENTRY_MSG_SPEC)
        ppp = StringMsgSpecParser(data)

        str_obj_model = ppp.parse()    # object model from string serialization

        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.MsgSpec))

        field_nbr = 0

        # XXX FAILS:
        self.round_trip_to_wire_format(
            chan, field_nbr, CoreTypes.MSG_SPEC, str_obj_model)

if __name__ == '__main__':
    unittest.main()
