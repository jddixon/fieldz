#!/usr/bin/env python3

# ~/dev/py/fieldz/testProtoSpec.py

##############################################
# XXX WARNING: ACTUAL ROUND TRIPS ARE DISABLED
##############################################

import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.field_impl import make_field_class         # added 2016-08-02
from fieldz.parser import StringProtoSpecParser
import fieldz.msg_spec as M
import fieldz.reg as reg
import wireops.typed as T
from wireops.field_types import FieldTypes, FieldStr

from fieldz.msg_impl import make_msg_class

# PROTOCOLS ---------------------------------------------------------
from fieldz.simple_protocol import SIMPLE_PROTOCOL
from fieldz.zoggery_proto_spec import ZOGGERY_PROTO_SPEC
from fieldz.nested_enum_proto_spec import NESTED_ENUM_PROTO_SPEC
from fieldz.nested_msgs_proto_spec import NESTED_MSGS_PROTO_SPEC

RNG = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestProtoSpec(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utilities #####################################################

    def le_msg_values(self):
        """ returns a list """
        timestamp = int(time.time())
        node_id = [0] * 20
        key = [0] * 20
        length = RNG.next_int32(256 * 256)
        # let's have some random bytes
        RNG.next_bytes(node_id)
        RNG.next_bytes(key)
        by_ = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        return [timestamp, node_id, key, length, by_, path]       # GEEP

    # actual unit tests #############################################

    def test_maps(self):
        max_ndx = FieldTypes.MAX_NDX
        max_name = FieldStr().as_str(max_ndx)
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

#   # GEEP
#   def doFieldTest(self, msgReg, name, fType, quantifier=M.Q_REQUIRED,
#                   fieldNbr=0, default=None):
#       # XXX Defaults are ignore for now.
#       f = M.FieldSpec(msgReg, name, fType, quantifier, fieldNbr, default)

#       self.assertEqual(name, f.name)
#       self.assertEqual(fType, f.fTypeNdx)
#       self.assertEqual(quantifier, f.quantifier)
#       self.assertEqual(fieldNbr, f.fieldNbr)
#       if default is not None:
#           self.assertEqual(default, f.default)

#       expectedRepr = "%s %s%s @%d \n" % (
#           name, f.fTypeName, M.qName(quantifier), fieldNbr)
#       # DEFAULTS NOT SUPPORTED
#       self.assertEqual(expectedRepr, f.__repr__())

#   def testsQuantifiers(self):
#       qName = M.qName
#       self.assertEqual('', qName(M.Q_REQUIRED))
#       self.assertEqual('?', qName(M.Q_OPTIONAL))
#       self.assertEqual('*', qName(M.Q_STAR))
#       self.assertEqual('+', qName(M.Q_PLUS))

#   def testFieldSpec(self):
#       protoName = 'org.xlattice.upax'
#       nodeReg = reg.NodeReg()
#       protoReg = reg.ProtoReg(protoName, nodeReg)
#       msgReg = reg.MsgReg(protoReg)

#       # default is not implemented yet
#       self.doFieldTest(msgReg, 'foo', FieldTypes._V_UINT32, M.Q_REQUIRED, 9)
#       self.doFieldTest(msgReg, 'bar', FieldTypes._V_SINT32, M.Q_STAR, 17)
#       self.doFieldTest(msgReg, 'nodeID', FieldTypes._F_BYTES20, M.Q_OPTIONAL, 92)
#       self.doFieldTest(msgReg, 'tix', FieldTypes._V_BOOL, M.Q_PLUS, 147)
#   # FOO

    def test_proto_spec(self):
        """ this is in fact the current spec for a log entry """
        proto_name = 'org.xlattice.upax'
        node_reg = reg.NodeReg()
        proto_reg = reg.ProtoReg(proto_name, node_reg)
        msg_reg = reg.MsgReg(proto_reg)
        proto_spec = M.ProtoSpec(proto_name, proto_reg)
        self.assertEqual(proto_name, proto_spec.name)
        parent = M.ProtoSpec(proto_name, proto_reg)

        msg_name = 'logEntry'
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
            M.FieldSpec(
                msg_reg,
                'length',
                FieldTypes.V_UINT32,
                M.Q_REQUIRED,
                3),
            M.FieldSpec(msg_reg, 'by_', FieldTypes.L_STRING, M.Q_REQUIRED, 4),
            M.FieldSpec(msg_reg, 'path', FieldTypes.L_STRING, M.Q_REQUIRED, 5),
        ]
        msg_spec = M.MsgSpec(msg_name, proto_spec, msg_reg)
        self.assertEqual(msg_name, msg_spec.name)
        for file in fields:
            msg_spec.add_field(file)

        proto_spec.add_msg(msg_spec)  # this was incorrectly commented out
        self.round_trip_poto_spec_via_string(proto_spec)             # GEEP

    def round_trip_poto_spec_via_string(self, match):
        """
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """
        canonical_spec = str(match.__repr__())
        # DEBUG
        print("\n### roundTrip: SPEC IN CANONICAL FORM:\n" + canonical_spec)
        print("### END SPEC IN CANONICAL FORM #######")
        # END
        ppp = StringProtoSpecParser(StringIO(canonical_spec))
        cloned_spec = ppp.parse()
        self.assertIsNone(cloned_spec.parent)    # created by default
        self.assertIsNotNone(cloned_spec.reg)

        # DEBUG
        clone_repr = cloned_spec.__repr__()
        print("### CLONED SPEC IN CANONICAL FORM:\n" + clone_repr)
        print("### END CLONED SPEC ##############")
        # END

        # crude tests of __eq__ AKA ==
        self.assertFalse(match is None)
        self.assertTrue(match == match)

        # one way of saying it ------------------
        self.assertTrue(match.__eq__(cloned_spec))

        self.assertTrue(cloned_spec.__eq__(match))
        # this is the same test -----------------
        self.assertTrue(match == cloned_spec)
        self.assertTrue(cloned_spec == match)

    def test_parse_and_write_proto_spec(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.zoggery', str_obj_model.name)
        self.assertEqual(0, len(str_obj_model.enums))
        self.assertEqual(1, len(str_obj_model.msgs))
        self.assertEqual(0, len(str_obj_model.seqs))

        msg_spec = str_obj_model.msgs[0]
        # XXX THIS SHOULD BE A LOOP, with no magic numbers
        self.assertEqual(msg_spec.f_name(0), 'timestamp')
        self.assertEqual(msg_spec.field_type_name(0), 'fuint32')
        self.assertEqual(msg_spec.f_name(1), 'nodeID')
        self.assertEqual(msg_spec.field_type_name(1), 'fbytes20')
        self.assertEqual(msg_spec.f_name(2), 'key')
        self.assertEqual(msg_spec.field_type_name(2), 'fbytes20')
        self.assertEqual(msg_spec.f_name(3), 'length')
        self.assertEqual(msg_spec.field_type_name(3), 'vuint32')
        self.assertEqual(msg_spec.f_name(4), 'by')
        self.assertEqual(msg_spec.field_type_name(4), 'lstring')
        self.assertEqual(msg_spec.f_name(5), 'path')
        self.assertEqual(msg_spec.field_type_name(5), 'lstring')      # GEEP

    def test_nested_enum(self):
        data = StringIO(NESTED_ENUM_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.ProtoSpec))

        self.assertEqual('org.xlattice.zoggery.ne', str_obj_model.name)
        self.assertEqual(1, len(str_obj_model.msgs))
        msg = str_obj_model.msgs[0]

        self.assertEqual('nestedEnums', msg.name)
        enums = msg.enums
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

#       self.roundTripProtoSpecViaString(sOM)       # GEEP

    def test_nested_msgs(self):
        """ XXX so far this is just testNestedEnum XXX """
        data = StringIO(NESTED_MSGS_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        str_obj_model = ppp.parse()             # object model from string serialization
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.ProtoSpec))

        self.assertEqual('org.xlattice.zoggery.nm', str_obj_model.name)
        self.assertEqual(1, len(str_obj_model.msgs))
        msg = str_obj_model.msgs[0]

        self.assertEqual('nestedMsgs', msg.name)
        enums = msg.enums
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

        self.round_trip_poto_spec_via_string(str_obj_model)

    # TEST CACHING --------------------------------------------------

    def test_caching(self):

        # SETUP
        data = StringIO(ZOGGERY_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        self.str_obj_model = ppp.parse()     # object model from string serialization
        self.proto_name = self.str_obj_model.name  # the dotted name of the protocol
        # END SETUp

        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        msg_spec = self.str_obj_model.msgs[0]
        name = msg_spec.name
        cls0 = make_msg_class(self.str_obj_model, name)
        cls1 = make_msg_class(self.str_obj_model, name)
        # we cache classe, so the two should be the same
        self.assertEqual(id(cls0), id(cls1))

        # chan = Channel(BUFSIZE)
        values = self.le_msg_values()
        le_msg0 = cls0(values)
        le_msg1 = cls0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(le_msg0), id(le_msg1))

        field_spec = msg_spec[0]
        dotted_name = "%s.%s" % (self.proto_name, msg_spec.name)
        f0cls = make_field_class(dotted_name, field_spec)
        f1cls = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(f0cls), id(f1cls))

if __name__ == '__main__':
    unittest.main()
