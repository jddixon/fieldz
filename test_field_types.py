#!/usr/bin/env python3

# testFieldTypes.py
import time
import unittest

from fieldz.field_types import FieldTypes, FieldStr

import fieldz.raw as R
import fieldz.typed as T
from rnglib import SimpleRNG


class TestFieldTypes(unittest.TestCase):
    """
    Actually tests the method used for instantiating and importing
    an instance of the FieldTypes class.
    """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i])
        print()

    # actual unit tests #############################################
    def test_constants(self):
        self.assertEqual(0, FieldTypes.V_BOOL)
        self.assertEqual(FieldStr.as_str(FieldTypes.V_BOOL), 'vbool')

        self.assertEqual(19, FieldTypes.F_BYTES32)
        self.assertEqual(FieldStr.as_str(FieldTypes.F_BYTES32), 'fbytes32')
        try:
            FieldTypes.V_BOOL = 47
        except AttributeError as exc:
            # 'success: caught attempt to reassign constant'
            pass

        for tstamp in range(FieldTypes.MAX_NDX + 1):
            type_name = FieldStr.as_str(tstamp)
            self.assertEqual(FieldStr.ndx(type_name), tstamp)

    def test_len_funcs(self):
        nnn = self.rng.next_int16()        # random field number
        ndx_ = self.rng.next_int16()        # random integer value

        # == varint types ===========================================
        len_ = R.field_hdr_len(nnn, FieldTypes.V_BOOL)
        self.assertEqual(len_ + 1, T.vbool_len(True, nnn))
        self.assertEqual(len_ + 1, T.vbool_len(False, nnn))

        len_ = R.field_hdr_len(nnn, FieldTypes.V_ENUM)
        zzz = len_ + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.venum_len(ndx_, nnn))
        # self.assertEqual( x, T.vEnumLen(-x, n) )

        ndx_ = self.rng.next_int32()
        self.assertTrue(ndx_ >= 0)

        len_ = R.field_hdr_len(nnn, FieldTypes.V_UINT32)
        zzz = len_ + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.vuint32_len(ndx_, nnn))

        ndx_ = self.rng.next_int32()
        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x80000000

        len_ = R.field_hdr_len(nnn, FieldTypes.V_SINT32)
        ppp = T.encode_sint32(ndx_)
        zzz = len_ + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint32_len(ndx_, nnn))

        ndx_ = self.rng.next_int64()
        self.assertTrue(ndx_ >= 0)

        len_ = R.field_hdr_len(nnn, FieldTypes.V_UINT64)
        zzz = len_ + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.vuint64_len(ndx_, nnn))

        ndx_ = self.rng.next_int64()
        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x8000000000000000

        len_ = R.field_hdr_len(nnn, FieldTypes.V_SINT64)
        ppp = T.encode_sint64(ndx_)
        zzz = len_ + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint64_len(ndx_, nnn))

        # == fixed length 4 byte ====================================
        ndx_ = self.rng.next_int64()        # value should be ignored

        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x8000000000000000

        # x is a signed 64 bit value whose value should be irrelevant
        len_ = R.field_hdr_len(nnn, FieldTypes.F_UINT32)
        self.assertEqual(len_ + 4, T.fuint32_len(ndx_, nnn))

        len_ = R.field_hdr_len(nnn, FieldTypes.F_SINT32)
        self.assertEqual(len_ + 4, T.fsint32_len(ndx_, nnn))

        len_ = R.field_hdr_len(nnn, FieldTypes.F_FLOAT)
        self.assertEqual(len_ + 4, T.ffloat_len(ndx_, nnn))

        # == fixed length 8 byte ====================================
        # n is that signed 64 bit value whose value should be irrelevant
        len_ = R.field_hdr_len(nnn, FieldTypes.F_UINT64)
        self.assertEqual(len_ + 8, T.fuint64_len(ndx_, nnn))
        len_ = R.field_hdr_len(nnn, FieldTypes.F_SINT64)
        self.assertEqual(len_ + 8, T.fsint64_len(ndx_, nnn))
        len_ = R.field_hdr_len(nnn, FieldTypes.F_DOUBLE)
        self.assertEqual(len_ + 8, T.fdouble_len(ndx_, nnn))

        # == LEN PLUS types =========================================
        def do_len_plus_test(ndx_, nnn):
            string = [0] * ndx_
            k = len(string)
            len_ = R.field_hdr_len(nnn, FieldTypes.L_BYTES)
            expected_len = len_ + R.length_as_varint(k) + k
            self.assertEqual(expected_len, T.lbytes_len(string, nnn))

        # -- lString ---------------------------------------
        string = self.rng.next_file_name(256)
        len_ = R.field_hdr_len(nnn, FieldTypes.L_STRING)
        k = len(string)
        expected_len = len_ + R.length_as_varint(k) + k
        self.assertEqual(expected_len, T.l_string_len(string, nnn))

        # -- lBytes ----------------------------------------
        do_len_plus_test(0x7f, nnn)
        do_len_plus_test(0x80, nnn)
        do_len_plus_test(0x3fff, nnn)
        do_len_plus_test(0x4000, nnn)

        # -- lMsg ------------------------------------------
        # XXX STUB

        # -- fixed length byte arrays -------------------------------
        buf = [0] * 512       # length functions should ignore actual size

        len_ = R.field_hdr_len(nnn, FieldTypes.F_BYTES16)
        self.assertEqual(len_ + 16, T.fbytes16_len(buf, nnn))

        len_ = R.field_hdr_len(nnn, FieldTypes.F_BYTES20)
        self.assertEqual(len_ + 20, T.fbytes20_len(buf, nnn))

        len_ = R.field_hdr_len(nnn, FieldTypes.F_BYTES32)
        self.assertEqual(len_ + 32, T.fbytes32_len(buf, nnn))

if __name__ == '__main__':
    unittest.main()
