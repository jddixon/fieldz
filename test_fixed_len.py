#!/usr/bin/env python3

# testFixedLen.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.chan import Channel
# from fieldz.raw import *

LEN_BUFF = 1024


class TestFixedLen (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i])
        print()

    def roundTrip32(self, nnn):
        """
        this tests writing and reading a 32-bit integer as the first and
        only field in a buffer
        """
        chan = Channel(LEN_BUFF)
        buf = chan.buffer

        # -- write 32-bit value -------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_b32_field(chan, nnn, field_nbr)
        chan.flip()

        # -- read 32-bit value --------------------------------------
        # first the header (which is a varint) ------------
        (fieldType, fieldNbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(B32_TYPE, fieldType)
        self.assertEqual(field_nbr, fieldNbr2)
        self.assertEqual(length_as_varint(field_hdr(field_nbr, B32_TYPE)),
                         offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b32(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 4, offset3)

    def roundTrip64(self, nnn):
        """
        this tests writing and reading a 64-bit integer as the first and
        only field in a buffer
        """
        chan = Channel(LEN_BUFF)
        buf = chan.buffer

        # -- write 64-bit value -------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_b64_field(chan, nnn, field_nbr)
        chan.flip()

#       # DEBUG
#       print "buffer after writing varint field: ",
#       self.dumpBuffer(buf)
#       # END

        # -- read 64-bit value --------------------------------------
        # first the header (which is a varint) ------------
        (fieldType, fieldNbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(B64_TYPE, fieldType)
        self.assertEqual(field_nbr, fieldNbr2)
        self.assertEqual(length_as_varint(field_hdr(field_nbr, B64_TYPE)),
                         offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b64(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 8, offset3)

    def testEncodeDecode(self):
        self.roundTrip32(0)
        self.roundTrip32(42)
        self.roundTrip32(0x7f)
        self.roundTrip32(0x80)
        self.roundTrip32(0x3fff)
        self.roundTrip32(0x4000)
        self.roundTrip32(0x1fffff)
        self.roundTrip32(0x200000)
        self.roundTrip32(0xfffffff)
        self.roundTrip32(0x10000000)
        self.roundTrip32(0xffffffff)

        self.roundTrip64(0)
        self.roundTrip64(42)
        self.roundTrip64(0x7f)
        self.roundTrip64(0x80)
        self.roundTrip64(0x3fff)
        self.roundTrip64(0x4000)
        self.roundTrip64(0x1fffff)
        self.roundTrip64(0x200000)
        self.roundTrip64(0xfffffff)
        self.roundTrip64(0x10000000)
        self.roundTrip64(0x7ffffffff)
        self.roundTrip64(0x800000000)
        self.roundTrip64(0x3ffffffffff)
        self.roundTrip64(0x40000000000)
        self.roundTrip64(0x1ffffffffffff)
        self.roundTrip64(0x2000000000000)
        self.roundTrip64(0xffffffffffffff)
        self.roundTrip64(0x100000000000000)
        self.roundTrip64(0x7fffffffffffffff)
        self.roundTrip64(0x8000000000000000)
        self.roundTrip64(0xffffffffffffffff)

if __name__ == '__main__':
    unittest.main()
