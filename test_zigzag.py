#!/usr/bin/env python3

# testTFReader.py
import time
import unittest
import ctypes

from rnglib import SimpleRNG
from fieldz.raw import *
# for encodeSint64
from fieldz.typed import *


class TestTFReader (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpBuffer(self, buf):
        for b in buf:
            print("0x%02x " % b, end=' ')
        print()

    # actual unit tests #############################################

    def testInt32s(self):
        v = 0xffffffff
        s32 = ctypes.c_int32(v).value
        self.assertEqual(-1, s32)
        u32 = ctypes.c_uint32(v).value
        self.assertEqual(256 * 256 * 256 * 256 - 1, u32)

        x = 0xffffff00
        v = ~x
        s32 = ctypes.c_int32(v).value
        self.assertEqual(0xff, s32)
        u32 = ctypes.c_uint32(v).value
        self.assertEqual(0xff, u32)

    def testInt64s(self):
        v = 0xffffffffffffffff
        s64 = ctypes.c_int64(v).value   # 'value' converts back to Python type
        self.assertEqual(-1, s64)
        u64 = ctypes.c_uint64(v).value
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

    def testVarintWithNegativeValues(self):
        # negative numbers, that is
        pass

    def doRoundTrip32(self, s):
        z = encodeSint32(s)
        s2 = decodeSint32(z)
        self.assertEqual(s, s2)

    def doRoundTrip64(self, s):
        z = encodeSint64(s)
        s2 = decodeSint64(z)
        self.assertEqual(s, s2)

    def testZZ32(self):
        self.doRoundTrip32(0)
        self.doRoundTrip32(-1)
        self.doRoundTrip32(1)
        self.doRoundTrip32(-2)
        self.doRoundTrip32(2)

        # XXX THIS VALUE CAUSES AN ERROR IN testTFWriter (returns -96)
        self.doRoundTrip32(-192)

        # XXX should do a few random numbers here instead
        self.doRoundTrip32(-15379)
        self.doRoundTrip32(15379)

        self.doRoundTrip32(-128 * 256 * 256 * 256)
        self.doRoundTrip32(128 * 256 * 256 * 256 - 1)

        # XXX need to also verify that sensible truncation takes place
        # if value doesn't actually fit in an int32

    def testZZ64(self):
        self.doRoundTrip64(0)
        self.doRoundTrip64(-1)
        self.doRoundTrip64(1)
        self.doRoundTrip64(-2)
        self.doRoundTrip64(2)

        self.doRoundTrip64(-128 * 256 * 256 * 256 * 256 * 256 * 256 * 256)
        self.doRoundTrip64(128 * 256 * 256 * 256 * 256 * 256 * 256 * 256 - 1)

if __name__ == '__main__':
    unittest.main()
