#!/usr/bin/env python3

# testFieldTypes.py
import time
import unittest

from fieldz.field_types import FieldTypes as F, FieldStr as FS

import fieldz.raw as R
import fieldz.typed as T
from rnglib import SimpleRNG


class TestFieldTypes (unittest.TestCase):
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
    def testConstants(self):
        f_types = FS()
        self.assertEqual(0, F.V_BOOL)
        self.assertEqual(f_types.as_str(F.V_BOOL), 'vbool')

        self.assertEqual(19, F.F_BYTES32)
        self.assertEqual(f_types.as_str(F.F_BYTES32), 'fbytes32')
        try:
            F.V_BOOL = 47
        except AttributeError as exc:
            # 'success: caught attempt to reassign constant'
            pass

        for tstamp in range(F.MAX_NDX + 1):
            type_name = FS.as_str(tstamp)
            self.assertEqual(f_types.ndx(type_name), tstamp)

    def testLenFuncs(self):
        nnn = self.rng.next_int16()        # random field number
        ndx_ = self.rng.next_int16()        # random integer value

        # == varint types ===========================================
        h = R.field_hdr_len(nnn, F.V_BOOL)
        self.assertEqual(h + 1, T.vbool_len(True, nnn))
        self.assertEqual(h + 1, T.vbool_len(False, nnn))

        h = R.field_hdr_len(nnn, F.V_ENUM)
        zzz = h + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.venum_len(ndx_, nnn))
        # self.assertEqual( x, T.vEnumLen(-x, n) )

        ndx_ = self.rng.next_int32()
        self.assertTrue(ndx_ >= 0)

        h = R.field_hdr_len(nnn, F.V_UINT32)
        zzz = h + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.vuint32_len(ndx_, nnn))

        ndx_ = self.rng.next_int32()
        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x80000000

        h = R.field_hdr_len(nnn, F.V_SINT32)
        ppp = T.encode_sint32(ndx_)
        zzz = h + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint32_len(ndx_, nnn))

        ndx_ = self.rng.next_int64()
        self.assertTrue(ndx_ >= 0)

        h = R.field_hdr_len(nnn, F.V_UINT64)
        zzz = h + R.length_as_varint(ndx_)
        self.assertEqual(zzz, T.vuint64_len(ndx_, nnn))

        ndx_ = self.rng.next_int64()
        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x8000000000000000

        h = R.field_hdr_len(nnn, F.V_SINT64)
        ppp = T.encode_sint64(ndx_)
        zzz = h + R.length_as_varint(ppp)
        self.assertEqual(zzz, T.vsint64_len(ndx_, nnn))

        # == fixed length 4 byte ====================================
        ndx_ = self.rng.next_int64()        # value should be ignored

        self.assertTrue(ndx_ >= 0)
        ndx_ = ndx_ - 0x8000000000000000

        # x is a signed 64 bit value whose value should be irrelevant
        h = R.field_hdr_len(nnn, F.F_UINT32)
        self.assertEqual(h + 4, T.fuint32_len(ndx_, nnn))

        h = R.field_hdr_len(nnn, F.F_SINT32)
        self.assertEqual(h + 4, T.fsint32_len(ndx_, nnn))

        h = R.field_hdr_len(nnn, F.F_FLOAT)
        self.assertEqual(h + 4, T.ffloat_len(ndx_, nnn))

        # == fixed length 8 byte ====================================
        # n is that signed 64 bit value whose value should be irrelevant
        h = R.field_hdr_len(nnn, F.F_UINT64)
        self.assertEqual(h + 8, T.fuint64_len(ndx_, nnn))
        h = R.field_hdr_len(nnn, F.F_SINT64)
        self.assertEqual(h + 8, T.fsint64_len(ndx_, nnn))
        h = R.field_hdr_len(nnn, F.F_DOUBLE)
        self.assertEqual(h + 8, T.fdouble_len(ndx_, nnn))

        # == LEN PLUS types =========================================
        def doLenPlusTest(ndx_, nnn):
            string = [0] * ndx_
            k = len(string)
            h = R.field_hdr_len(nnn, F.L_BYTES)
            expectedLen = h + R.length_as_varint(k) + k
            self.assertEqual(expectedLen, T.lbytes_len(string, nnn))

        # -- lString ---------------------------------------
        string = self.rng.next_file_name(256)
        h = R.field_hdr_len(nnn, F.L_STRING)
        k = len(string)
        expectedLen = h + R.length_as_varint(k) + k
        self.assertEqual(expectedLen, T.l_string_len(string, nnn))

        # -- lBytes ----------------------------------------
        doLenPlusTest(0x7f, nnn)
        doLenPlusTest(0x80, nnn)
        doLenPlusTest(0x3fff, nnn)
        doLenPlusTest(0x4000, nnn)

        # -- lMsg ------------------------------------------
        # XXX STUB

        # -- fixed length byte arrays -------------------------------
        buf = [0] * 512       # length functions should ignore actual size

        h = R.field_hdr_len(nnn, F.F_BYTES16)
        self.assertEqual(h + 16, T.fbytes16_len(buf, nnn))

        h = R.field_hdr_len(nnn, F.F_BYTES20)
        self.assertEqual(h + 20, T.fbytes20_len(buf, nnn))

        h = R.field_hdr_len(nnn, F.F_BYTES32)
        self.assertEqual(h + 32, T.fbytes32_len(buf, nnn))

if __name__ == '__main__':
    unittest.main()
