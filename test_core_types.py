#!/usr/bin/env python3

# testCoreTypes.py
# import time
import unittest
from io import StringIO

from fieldz.chan import Channel
from fieldz.raw import(
    # VARINT_TYPE,                            # PACKED_VARINT_TYPE,
    #B32_TYPE, B64_TYPE,
    LEN_PLUS_TYPE,
    # B128_TYPE, B160_TYPE, B256_TYPE,

    # field_hdr,
    field_hdr_len,
    read_field_hdr,
    # hdr_field_nbr, hdr_type,
    # length_as_varint, write_varint_field,
    #read_raw_varint, write_raw_varint,
    # read_raw_b32,           # write_b32_field,
    # read_raw_b64,           # write_b64_field,
    # read_raw_len_plus,      # write_len_plus_field,
    # read_raw_b128,          # write_b128_field,
    # read_raw_b160,          # write_b160_field,
    # read_raw_b256,          # write_b256_field,
    # next_power_of_two,
    # WireBuffer,
)
import fieldz.msg_spec as M
from fieldz.core_types import CoreTypes
from fieldz.field_types import FieldTypes
from fieldz.reg import NodeReg, ProtoReg, MsgReg
from fieldz.parser import StringMsgSpecParser

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
        self.assertEqual(5, CoreTypes.max_ndx)
        self.assertEqual(0, CoreTypes.ENUM_PAIR_SPEC)
        self.assertEqual(5, CoreTypes.PROTO_SPEC)

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
        ret_val = getter(msg_reg, chan)

        # gets the same error:ret_val = M.cGetFuncs[c_type](chan)

        r_pos = chan.position
        # DEBUG
        print("  ROUND TRIP: val    = %s" % val)
        print("              ret_val = %s" % ret_val)
        # END
        self.assertEqual(val, ret_val)

    def test_round_tripping_core_types(self):
        buf_size = 16 * 1024
        chan = Channel(buf_size)

        # -----------------------------------------------------------
        # XXX FAILS if msgReg arg added: WRONG NUMBER OF ARGS
        # XXX n=0 is wired into round_trip_to_wire_format XXX
        nnn = 0                           # 0-based field number
        string = M.EnumPairSpec('funnyFarm', 497)
        self.round_trip_to_wire_format(
            chan, nnn, CoreTypes.ENUM_PAIR_SPEC, string)

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
#       self.round_trip_to_wire_format( chan, n, CoreTypes.ENUM_SPEC, s)

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
        # XXX FAILS: invalid (optionlly dotted) name 'bytearray(b'jollyGood')
        self.round_trip_to_wire_format(chan, nnn, CoreTypes.FIELD_SPEC, string)

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
        self.round_trip_to_wire_format(
            chan, nnn, CoreTypes.MSG_SPEC, str_obj_model)


if __name__ == '__main__':
    unittest.main()
