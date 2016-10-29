#!/usr/bin/env python3

# testTFReader.py
import time
import unittest
import ctypes

from rnglib import SimpleRNG
# from fieldz.raw import *
from fieldz.typed import(
    encode_sint32, encode_sint64, decode_sint32, decode_sint64)


class TestTFReader(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dump_buffer(self, buf):
        for b_val in buf:
            print("0x%02x " % b_val, end=' ')
        print()

    # actual unit tests #############################################

    def test_int32s(self):
        varint_ = 0xffffffff
        s32 = ctypes.c_int32(varint_).value
        self.assertEqual(-1, s32)
        u32 = ctypes.c_uint32(varint_).value
        self.assertEqual(256 * 256 * 256 * 256 - 1, u32)

        ndx_ = 0xffffff00
        varint_ = ~ndx_
        s32 = ctypes.c_int32(varint_).value
        self.assertEqual(0xff, s32)
        u32 = ctypes.c_uint32(varint_).value
        self.assertEqual(0xff, u32)

    def test_int64s(self):
        varint_ = 0xffffffffffffffff
        # 'value' converts back to Python type
        s64 = ctypes.c_int64(varint_).value
        self.assertEqual(-1, s64)
        u64 = ctypes.c_uint64(varint_).value
        self.assertEqual(
            256 *
            256 *
            256 *
            256 *
            256 *
            256 *
            256 *
            256 -
            1,
            u64)

    def test_varint_with_negative_values(self):
        # negative numbers, that is
        pass

    def do_round_trip32(self, string):
        zzz = encode_sint32(string)
        string2 = decode_sint32(zzz)
        self.assertEqual(string, string2)

    def do_round_trip64(self, string):
        zzz = encode_sint64(string)
        string2 = decode_sint64(zzz)
        self.assertEqual(string, string2)

    def test_zz32(self):
        self.do_round_trip32(0)
        self.do_round_trip32(-1)
        self.do_round_trip32(1)
        self.do_round_trip32(-2)
        self.do_round_trip32(2)

        # XXX THIS VALUE CAUSES AN ERROR IN testTFWriter (returns -96)
        self.do_round_trip32(-192)

        # XXX should do a few random numbers here instead
        self.do_round_trip32(-15379)
        self.do_round_trip32(15379)

        self.do_round_trip32(-128 * 256 * 256 * 256)
        self.do_round_trip32(128 * 256 * 256 * 256 - 1)

        # XXX need to also verify that sensible truncation takes place
        # if value doesn't actually fit in an int32

    def test_zz64(self):
        self.do_round_trip64(0)
        self.do_round_trip64(-1)
        self.do_round_trip64(1)
        self.do_round_trip64(-2)
        self.do_round_trip64(2)

        self.do_round_trip64(-128 * 256 * 256 * 256 * 256 * 256 * 256 * 256)
        self.do_round_trip64(128 * 256 * 256 * 256 * 256 * 256 * 256 * 256 - 1)

if __name__ == '__main__':
    unittest.main()
