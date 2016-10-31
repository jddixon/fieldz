#!/usr/bin/env python3

# testMsgSpec.py

import time
import unittest
from io import StringIO

from rnglib import SimpleRNG


from fieldz.field_types import FieldTypes, FieldStr

from fieldz.parser import StringMsgSpecParser
import fieldz.msg_spec as M
import fieldz.typed as T
import fieldz.reg as R

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

MULTI_ENUM_MSG_SPEC = u"""
# protocol org.xlattice.zoggery
message multiEnum
 enum Foo
  a = 1
  b = 2

 enum Bar
  c = 3
  d = 4
  e = 5

 whatever    vuint32?
 cantImagine vsint32+
 # NEXT LINES FAIL
 xxx         Foo
 yyy         Bar

"""


class TestMsgSpec(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_registries(self, protocol):
        node_reg = R.NodeReg()
        proto_reg = R.ProtoReg(protocol, node_reg)
        msg_reg = R.MsgReg(proto_reg)
        return (node_reg, proto_reg, msg_reg)

    # actual unit tests #############################################

    def test_maps(self):
        max_ndx = FieldTypes.MAX_NDX
        max_name = FieldStr.as_str(max_ndx)
        self.assertEqual('fbytes32', max_name)

    def test_enum(self):
        """
        A not very useful enum, limited to mapping a fixed list of
        names into a zero-based sequence of integers.
        """

        # XXX should test null or empty lists, ill-formed names
        name = 'george'
        pairs = [('abc', 3), ('def', 5), ('ghi', 7)]
        enum = M.EnumSpec.create(name, pairs)
        # self.assertEqual( ','.join(pairs), enum.__repr__())
        self.assertEqual(3, enum.value('abc'))
        self.assertEqual(5, enum.value('def'))
        self.assertEqual(7, enum.value('ghi'))

    # FOO
    def do_field_test(self, name, field_type, quantifier=M.Q_REQUIRED,
                      field_nbr=0, default=None):
        node_reg, proto_reg, msg_reg = self.make_registries(
            'org.xlattice.fieldz.test.fieldSpec')

        # XXX Defaults are ignore for now.
        file = M.FieldSpec(
            msg_reg,
            name,
            field_type,
            quantifier,
            field_nbr,
            default)

        self.assertEqual(name, file.name)
        self.assertEqual(field_type, file.field_type_ndx)
        self.assertEqual(quantifier, file.quantifier)
        self.assertEqual(field_nbr, file.field_nbr)
        if default is not None:
            self.assertEqual(default, file.default)

        expected_repr = "%s %s%s @%d \n" % (
            name, file.field_type_name, M.q_name(quantifier), field_nbr)
        # DEFAULTS NOT SUPPORTED
        self.assertEqual(expected_repr, file.__repr__())

    def test_quantifiers(self):
        q_name = M.q_name
        self.assertEqual('', q_name(M.Q_REQUIRED))
        self.assertEqual('?', q_name(M.Q_OPTIONAL))
        self.assertEqual('*', q_name(M.Q_STAR))
        self.assertEqual('+', q_name(M.Q_PLUS))

    def test_field_spec(self):
        # default is not implemented yet
        self.do_field_test('foo', FieldTypes.V_UINT32, M.Q_REQUIRED, 9)
        self.do_field_test('bar', FieldTypes.V_SINT32, M.Q_STAR, 17)
        self.do_field_test('node_id', FieldTypes.F_BYTES20, M.Q_OPTIONAL, 92)
        self.do_field_test('tix', FieldTypes.V_BOOL, M.Q_PLUS, 147)

    # GEEP

    def round_trip_msg_spec_via_str(self, match, protocol):
        """
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """

        # should be unicode
        canonical_spec = match.__repr__()
        # DEBUG
        print("Type of m: ", type(match))
        print("CANONICAL SPEC:\n" + canonical_spec)
        # END

        node_reg = R.NodeReg()
        proto_reg = R.ProtoReg(protocol, node_reg)
        ppp = StringMsgSpecParser(StringIO(canonical_spec))

        # XXX FAILS: protoSpec has ill-formed protocol line
        cloned_spec = ppp.parse()

        self.assertIsNotNone(cloned_spec)
        # DEBUG =======================
        print('CLONED SPEC:\n' + cloned_spec.__repr__())
        # END =========================
        # crude tests of __eq__ AKA ==
        self.assertFalse(match is None)
        self.assertTrue(match == match)

        # one way of saying it ------------------
        self.assertTrue(match.__eq__(cloned_spec))
        self.assertTrue(cloned_spec.__eq__(match))
        # this is the same test -----------------
        self.assertTrue(match == cloned_spec)
        self.assertTrue(cloned_spec == match)                # FOO

    def test_msg_spec(self):
        """ this is in fact the current spec for a log entry """
        protocol = 'org.xlattice.upax'
        node_reg, proto_reg, msg_reg = self.make_registries(protocol)
        # dummy:
        parent = M.ProtoSpec(protocol, proto_reg)

        # the enum is not used
        enum = M.EnumSpec.create('Joe', [
            ('oh', 92), ('hello', 47), ('there', 322), ])
        fields = [
            M.FieldSpec(
                msg_reg,
                'timestamp',
                FieldTypes.F_UINT32,
                M.Q_REQUIRED,
                0),
            M.FieldSpec(
                msg_reg,
                'node_id',
                FieldTypes.F_BYTES20,
                M.Q_REQUIRED,
                1),
            M.FieldSpec(msg_reg, 'key', FieldTypes.F_BYTES20, M.Q_REQUIRED, 2),
            M.FieldSpec(msg_reg, 'by', FieldTypes.L_STRING, M.Q_REQUIRED, 3),
            M.FieldSpec(msg_reg, 'path', FieldTypes.L_STRING, M.Q_REQUIRED, 4),
        ]
        name = 'logEntry'
        msg_spec = M.MsgSpec(name, protocol, msg_reg)
        for file in fields:
            msg_spec.add_field(file)
        msg_spec.add_enum(enum)

        self.assertEqual(name, msg_spec.name)

        # XXX DEPRECATED
        self.assertEqual(len(fields), len(msg_spec))
        for i in range(len(msg_spec)):
            self.assertEqual(fields[i].name, msg_spec.f_name(i))
            self.assertEqual(
                fields[i].field_type_name,
                msg_spec.field_type_name(i))
        # END DEPRECATED

        self.assertEqual(len(fields), len(msg_spec))
        i = 0
        for field in msg_spec:
            self.assertEqual(fields[i].name, field._name)
            self.assertEqual(fields[i].field_type_ndx, field.field_type_ndx)
            i += 1

        self.round_trip_msg_spec_via_str(
            msg_spec, protocol)                 # BAZ

    def test_parse_and_write_msg_spec(self):
        data = StringIO(LOG_ENTRY_MSG_SPEC)
        ppp = StringMsgSpecParser(data)   # data should be file-like
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.MsgSpec))

        self.assertEqual('logEntry', str_obj_model.name)

        # XXX THIS SHOULD BE A LOOP, with no magic numbers
        self.assertEqual(str_obj_model.f_name(0), 'timestamp')
        self.assertEqual(str_obj_model.field_type_name(0), 'fuint32')
        self.assertEqual(str_obj_model.f_name(1), 'nodeID')
        self.assertEqual(str_obj_model.field_type_name(1), 'fbytes20')
        self.assertEqual(str_obj_model.f_name(2), 'key')
        self.assertEqual(str_obj_model.field_type_name(2), 'fbytes20')
        self.assertEqual(str_obj_model.f_name(3), 'length')
        self.assertEqual(str_obj_model.field_type_name(3), 'vuint32')
        self.assertEqual(str_obj_model.f_name(4), 'by')
        self.assertEqual(str_obj_model.field_type_name(4), 'lstring')
        self.assertEqual(str_obj_model.f_name(5), 'path')
        self.assertEqual(
            str_obj_model.field_type_name(5),
            'lstring')          # BAR

    def test_multi_enum(self):
        protocol = 'org.xlattice.fieldz.test.multiEnum'

        data = StringIO(MULTI_ENUM_MSG_SPEC)
        ppp = StringMsgSpecParser(data)   # data should be file-like
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.MsgSpec))

        # self.assertEqual( 'org.xlattice.zoggery', sOM.protocol )
        self.assertEqual('multiEnum', str_obj_model.name)

        enums = str_obj_model.enums
        self.assertIsNotNone(enums)
        self.assertEqual(2, len(enums))

        foo_enum = enums[0]
        bar_enum = enums[1]
        self.assertEqual('Foo', foo_enum.name)
        self.assertEqual('Bar', bar_enum.name)

        self.assertEqual(2, len(foo_enum))
        self.assertEqual(3, len(bar_enum))

        a_pair = foo_enum[0]
        self.assertEqual('aVal', a_pair.symbol)
        self.assertEqual(1, a_pair.value)

        b_pair = foo_enum[1]
        self.assertEqual('b_val', b_pair.symbol)
        self.assertEqual(2, b_pair.value)

        c_pair = bar_enum[0]
        self.assertEqual('cVal', c_pair.symbol)
        self.assertEqual(3, c_pair.value)

        d_pair = bar_enum[1]
        self.assertEqual('dVal', d_pair.symbol)
        self.assertEqual(4, d_pair.value)

        e_pair = bar_enum[2]
        self.assertEqual('exc', e_pair.symbol)
        self.assertEqual(5, e_pair.value)

        self.round_trip_msg_spec_via_str(
            str_obj_model, protocol)             # GEEP

if __name__ == '__main__':
    unittest.main()
