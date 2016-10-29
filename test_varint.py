#!/usr/bin/env python3

# testVarint.py
import time
import unittest

from rnglib import SimpleRNG
# from fieldz.raw import *

from fieldz.raw import(
    VARINT_TYPE,                            # PACKED_VARINT_TYPE,
    #B32_TYPE, B64_TYPE, LEN_PLUS_TYPE,
    #B128_TYPE, B160_TYPE, B256_TYPE,

    # field_hdr, field_hdr_len,
    read_field_hdr,
    # hdr_field_nbr, hdr_type,
    length_as_varint, write_varint_field,
    read_raw_varint,  # write_raw_varint,
    # read_raw_b32,           # write_b32_field,
    # read_raw_b64,           # write_b64_field,
    # read_raw_len_plus,      # write_len_plus_field,
    # read_raw_b128,          # write_b128_field,
    # read_raw_b160,          # write_b160_field,
    # read_raw_b256,          # write_b256_field,
    # next_power_of_two,
    # WireBuffer,
)
from fieldz.chan import Channel

LEN_BUFFER = 1024


class TestVarint(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def test_length_as_varint(self):
        len_ = length_as_varint
        self.assertEqual(1, len_(0))
        self.assertEqual(1, len_(0x7f))
        self.assertEqual(2, len_(0x80))
        self.assertEqual(2, len_(0x3fff))
        self.assertEqual(3, len_(0x4000))
        self.assertEqual(3, len_(0x1fffff))
        self.assertEqual(4, len_(0x200000))
        self.assertEqual(4, len_(0xfffffff))
        self.assertEqual(5, len_(0x10000000))
        self.assertEqual(5, len_(0x7ffffffff))
        self.assertEqual(6, len_(0x800000000))
        self.assertEqual(6, len_(0x3ffffffffff))
        self.assertEqual(7, len_(0x40000000000))
        self.assertEqual(7, len_(0x1ffffffffffff))
        self.assertEqual(8, len_(0x2000000000000))
        self.assertEqual(8, len_(0xffffffffffffff))
        self.assertEqual(9, len_(0x100000000000000))
        self.assertEqual(9, len_(0x7fffffffffffffff))
        self.assertEqual(10, len_(0x8000000000000000))
        # the next test fails if I don't parenthesize the shift term or
        # convert >1 to /2
        big_number = 0x80000000000000000 + (self.rng.next_int64() > 1)
        self.assertEqual(10, len(big_number))

        # MAKE SURE THIS WORKS WITH SIGNED NUMBERS

    def round_trip(self, nnn):
        """
        this tests writing and reading a varint as the first and
        only field in a buffer
        """
        # -- write varint -------------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        chan = Channel(LEN_BUFFER)
        buf = chan.buffer
        offset = write_varint_field(chan, nnn, field_nbr)
        chan.flip()

        # -- read varint --------------------------------------------
        # first the header (which is a varint) ------------
        (prim_type, field_nbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(VARINT_TYPE, prim_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_nbr << 3), offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_varint(chan)
        chan.flip()
        offset3 = chan.limit
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + length_as_varint(nnn), offset3)

    def test_encode_decode(self):
        """
        All varints are handled as 64 bit unsigned ints.  WE MAY SOMETIMES
        WANT TO RESTRICT THEM TO uint32s.  Other than 42, these are the
        usual border values.
        """
        self.round_trip(0)
        self.round_trip(42)
        self.round_trip(0x7f)
        self.round_trip(0x80)
        self.round_trip(0x3fff)
        self.round_trip(0x4000)
        self.round_trip(0x1fffff)
        self.round_trip(0x200000)
        self.round_trip(0xfffffff)
        self.round_trip(0x10000000)
        self.round_trip(0x7ffffffff)
        self.round_trip(0x800000000)
        self.round_trip(0x3ffffffffff)
        self.round_trip(0x40000000000)
        self.round_trip(0x1ffffffffffff)
        self.round_trip(0x2000000000000)
        self.round_trip(0xffffffffffffff)
        self.round_trip(0x100000000000000)
        self.round_trip(0x7fffffffffffffff)
        self.round_trip(0x8000000000000000)
        self.round_trip(0xffffffffffffffff)


if __name__ == '__main__':
    unittest.main()
