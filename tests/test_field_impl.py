#!/usr/bin/env python3

# ~/dev/py/fieldz/testFieldImpl.py

import time
import unittest
from io import StringIO

from fieldz.enum import Quants
from rnglib import SimpleRNG

from fieldz import reg
#from fieldz.parser import StringProtoSpecParser
import fieldz.msg_spec as M

from fieldz.field_impl import make_field_class

#from fieldz.msg_impl import makeMsgClass, makeFieldClass, MsgImpl
#from wireops.chan import Channel
#import wireops.typed as T

from wireops.enum import PrimTypes, FieldTypes
from wireops.raw import write_field_hdr, write_raw_varint

PROTOCOL_UNDER_TEST = 'org.xlattice.fieldz.test.field_spec'
MSG_UNDER_TEST = 'myTestMsg'

BUFSIZE = 16 * 1024


class TestFieldImpl(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

#       data = StringIO(ZOGGERY_PROTO_SPEC)
#       p = StringProtoSpecParser(data)   # data should be file-like
#       self.str_obj_model = p.parse()     # object model from string serialization
# self.proto_name = self.str_obj_model.name  # the dotted name of the
# protocol

    def tearDown(self):
        pass

    # utility functions #############################################

    def make_registries(self, protocol):
        node_reg = reg.NodeReg()
        proto_reg = reg.ProtoReg(protocol, node_reg)
        msg_reg = reg.MsgReg(proto_reg)
        return (node_reg, proto_reg, msg_reg)

    def le_msg_values(self):
        """ returns a list """
        timestamp = int(time.time())
        node_id = [0] * 20
        key = [0] * 20
        length = self.rng.next_int32(256 * 256)
        # let's have some random bytes
        self.rng.next_bytes(node_id)
        self.rng.next_bytes(key)
        by_ = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        return [timestamp, node_id, key, length, by_, path]

    def lil_big_msg_values(self):
        """
        This returns a list of random-ish values in order by field type
        so that values[_F_FLOAT], for example, is a random float value.
        """
        values = []

        # 2016-03-30 This is NOT in sync with littleBigTest.py,
        #   because I have added a None for lMsg at _L_MSG

        values.append(self.rng.next_boolean())       # vBoolReqField         0
        values.append(self.rng.next_int16())         # vEnumReqField         1

        values.append(self.rng.next_int32())         # vInt32ReqField        2
        values.append(self.rng.next_int64())         # vInt64ReqField        3

        values.append(self.rng.next_int32())         # vuInt32ReqField       4
        values.append(self.rng.next_int32())         # vuInt64ReqField       5
        values.append(self.rng.next_int64())         # vsInt32ReqField       6
        values.append(self.rng.next_int64())         # vsInt64ReqField       7

        values.append(self.rng.next_int32())         # fsInt32ReqField       8
        values.append(self.rng.next_int32())         # fuInt32ReqField       9
        values.append(self.rng.next_real())          # fFloatReqField        10

        values.append(self.rng.next_int64())         # fsInt64ReqField       11
        values.append(self.rng.next_int64())         # fuInt64ReqField       12

        values.append(self.rng.next_real())          # fDoubleReqField       13

        # lStringReqField       14
        values.append(self.rng.next_file_name(16))

        rnd_len = 16 + self.rng.next_int16(49)
        byte_buf = bytearray(rnd_len)
        self.rng.next_bytes(byte_buf)
        values.append(bytes(byte_buf))               # lBytesReqField        15

        values.append(None)                         # <-------- for lMsg    16

        b128_buf = bytearray(16)
        self.rng.next_bytes(b128_buf)
        values.append(bytes(b128_buf))               # fBytes16ReqField      17

        b160_buf = bytearray(20)
        self.rng.next_bytes(b160_buf)
        values.append(bytes(b160_buf))               # fBytes20ReqField      18

        b256_buf = bytearray(32)
        self.rng.next_bytes(b256_buf)
        values.append(bytes(b256_buf))               # fBytes32ReqField      19

        return values

    # actual unit tests #############################################

    def check_field_impl_against_spec(
            # msg_name not actually tested
            self, proto_name, msg_name, field_spec, value):    # significant
        self.assertIsNotNone(field_spec)
        # DEBUG
        print("check_field_impl_against_spec: field_spec is a ",
              type(field_spec))
        # END
        dotted_name = "%s.%s" % (proto_name, msg_name)
        cls = make_field_class(dotted_name, field_spec)         # a class
        if '__dict__' in dir(cls):
            print('\nGENERATED FieldImpl CLASS DICTIONARY')
            for key in list(cls.__dict__.keys()):
                print("  %-20s %s" % (key, cls.__dict__[key]))

        self.assertIsNotNone(cls)
        fld = cls(value)                                      # an instance
        self.assertIsNotNone(fld)
        self.assertTrue(isinstance(fld, cls))

        # instance attributes -----------------------------
        # we verify that the properties work correctly

        # pylint: disable=no-member
        self.assertEqual(field_spec.name, fld.name)
        self.assertEqual(field_spec.field_type, fld.field_type)
        self.assertEqual(field_spec.quantifier, fld.quantifier)
        self.assertEqual(field_spec.field_nbr, fld.field_nbr)
        self.assertIsNone(fld.default)          # not an elegant test

        # instance attribute ------------------------------
        # we can read back the value assigned to the instance

        self.assertEqual(value, fld.value)

        # with slots enabled, this is never seen ----------
        # because __dict__ is not in the list of valid
        # attributes for f
        if '__dict__' in dir(fld):
            print('\nGENERATED FieldImpl INSTANCE DICTIONARY')
            for item in list(fld.__dict__.keys()):
                print("%-20s %s" % (item, fld.__dict__[item]))

    def test_field_impl(self):

        node_reg, proto_reg, msg_reg = self.make_registries(
            PROTOCOL_UNDER_TEST)
        values = self.lil_big_msg_values()

        # DEBUG
        print("testFieldImpl: there are %d values" % len(values))
        # END

        # There are 18 values corresponding to the 18 field types;
        # _L_MSG should be skipped

        # pylint: disable=not-an-iterable
        for ftype in FieldTypes:
            # DEBUG
            print("testFieldImpl: ftype = %s (%d)" % (ftype.sym, ftype.value))
            # END
            # pylint: disable=no-member
            if ftype == FieldTypes.L_MSG:
                continue

            # default quantifier is Quants.REQUIRED, default is None

            field_name = 'field%d' % ftype.value
            field_spec = M.FieldSpec(
                msg_reg, field_name, ftype, field_nbr=ftype.value + 100)

            self.check_field_impl_against_spec(
                PROTOCOL_UNDER_TEST, MSG_UNDER_TEST,
                field_spec, values[ftype.value])

    # TEST FIELD SPEC -----------------------------------------------

    # pylint: disable=no-member
    def do_field_spec_test(self, name, field_type, quantifier=Quants.REQUIRED,
                           field_nbr=0, default=None):

        node_reg, proto_reg, msg_reg = self.make_registries(
            PROTOCOL_UNDER_TEST)

        # XXX Defaults are ignored for now.
        fld = M.FieldSpec(
            msg_reg,
            name,
            field_type,
            quantifier,
            field_nbr,
            default)

        self.assertEqual(name, fld.name)
        self.assertEqual(field_type, fld.field_type)
        self.assertEqual(quantifier, fld.quantifier)
        self.assertEqual(field_nbr, fld.field_nbr)
        if default is not None:
            self.assertEqual(default, fld.default)

        expected_repr = "%s %s%s @%d \n" % (
            name, fld.field_type_name, quantifier.sym, field_nbr)
        # DEFAULTS NOT SUPPORTED
        self.assertEqual(expected_repr, fld.__repr__())

    def test_field_spec(self):
        # default is not implemented yet
        # pylint: disable=no-member
        self.do_field_spec_test('foo', FieldTypes.V_UINT32, Quants.REQUIRED, 9)
        self.do_field_spec_test('bar', FieldTypes.V_SINT32, Quants.STAR, 17)
        self.do_field_spec_test(
            'node_id',
            FieldTypes.F_BYTES20,
            Quants.OPTIONAL,
            92)
        self.do_field_spec_test('tix', FieldTypes.V_BOOL, Quants.PLUS, 147)


if __name__ == '__main__':
    unittest.main()
