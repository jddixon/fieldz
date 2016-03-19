#!/usr/bin/python3

# testVarint.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.raw import *
from fieldz.chan import *

LEN_BUFFER = 1024


class TestVarint (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpBuffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def testLengthAsVarint(self):
        len = lengthAsVarint
        self.assertEqual(1, len(0))
        self.assertEqual(1, len(0x7f))
        self.assertEqual(2, len(0x80))
        self.assertEqual(2, len(0x3fff))
        self.assertEqual(3, len(0x4000))
        self.assertEqual(3, len(0x1fffff))
        self.assertEqual(4, len(0x200000))
        self.assertEqual(4, len(0xfffffff))
        self.assertEqual(5, len(0x10000000))
        self.assertEqual(5, len(0x7ffffffff))
        self.assertEqual(6, len(0x800000000))
        self.assertEqual(6, len(0x3ffffffffff))
        self.assertEqual(7, len(0x40000000000))
        self.assertEqual(7, len(0x1ffffffffffff))
        self.assertEqual(8, len(0x2000000000000))
        self.assertEqual(8, len(0xffffffffffffff))
        self.assertEqual(9, len(0x100000000000000))
        self.assertEqual(9, len(0x7fffffffffffffff))
        self.assertEqual(10, len(0x8000000000000000))
        # the next test fails if I don't parenthesize the shift term or
        # convert >1 to /2
        bigNumber = 0x80000000000000000 + (self.rng.nextInt64() > 1)
        self.assertEqual(10, len(bigNumber))

        # MAKE SURE THIS WORKS WITH SIGNED NUMBERS

    def roundTrip(self, n):
        """
        this tests writing and reading a varint as the first and
        only field in a buffer
        """
        # -- write varint -------------------------------------------
        fieldNbr = 1 + self.rng.nextInt16(1024)
        chan = Channel(LEN_BUFFER)
        buf = chan.buffer
        offset = writeVarintField(chan, n, fieldNbr)
        chan.flip()

        # -- read varint --------------------------------------------
        # first the header (which is a varint) ------------
        (primType, fieldNbr2) = readFieldHdr(chan)
        offset2 = chan.position
        self.assertEqual(VARINT_TYPE, primType)
        self.assertEqual(fieldNbr, fieldNbr2)
        self.assertEqual(lengthAsVarint(fieldNbr << 3), offset2)

        # then the varint proper --------------------------
        v = readRawVarint(chan)
        chan.flip()
        offset3 = chan.limit
        self.assertEqual(n, v)
        self.assertEqual(offset2 + lengthAsVarint(n), offset3)

    def testEncodeDecode(self):
        """
        All varints are handled as 64 bit unsigned ints.  WE MAY SOMETIMES
        WANT TO RESTRICT THEM TO uint32s.  Other than 42, these are the
        usual border values.
        """
        self.roundTrip(0)
        self.roundTrip(42)
        self.roundTrip(0x7f)
        self.roundTrip(0x80)
        self.roundTrip(0x3fff)
        self.roundTrip(0x4000)
        self.roundTrip(0x1fffff)
        self.roundTrip(0x200000)
        self.roundTrip(0xfffffff)
        self.roundTrip(0x10000000)
        self.roundTrip(0x7ffffffff)
        self.roundTrip(0x800000000)
        self.roundTrip(0x3ffffffffff)
        self.roundTrip(0x40000000000)
        self.roundTrip(0x1ffffffffffff)
        self.roundTrip(0x2000000000000)
        self.roundTrip(0xffffffffffffff)
        self.roundTrip(0x100000000000000)
        self.roundTrip(0x7fffffffffffffff)
        self.roundTrip(0x8000000000000000)
        self.roundTrip(0xffffffffffffffff)


if __name__ == '__main__':
    unittest.main()
