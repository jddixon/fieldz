#!/usr/bin/env python3

# testFixedLen.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.chan import Channel
from fieldz.raw import(
    # VARINT_TYPE,                            # PACKED_VARINT_TYPE,
    B32_TYPE, B64_TYPE,
    # LEN_PLUS_TYPE,
    # B128_TYPE, B160_TYPE, B256_TYPE,

    field_hdr,  # field_hdr_len,
    read_field_hdr,
    # hdr_field_nbr, hdr_type,
    length_as_varint,  # write_varint_field,
    #read_raw_varint, write_raw_varint,
    read_raw_b32,
    write_b32_field,
    read_raw_b64,
    write_b64_field,
    # read_raw_len_plus,      # write_len_plus_field,
    # read_raw_b128,          # write_b128_field,
    # read_raw_b160,          # write_b160_field,
    # read_raw_b256,          # write_b256_field,
    # next_power_of_two,
    # WireBuffer,
)

LEN_BUFF = 1024


class TestFixedLen(unittest.TestCase):

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

    def round_trip32(self, nnn):
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
        (field_type, field_nbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(B32_TYPE, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_hdr(field_nbr, B32_TYPE)),
                         offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b32(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 4, offset3)

    def round_trip64(self, nnn):
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
        (field_type, field_nbr2) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(B64_TYPE, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_hdr(field_nbr, B64_TYPE)),
                         offset2)

        # then the varint proper --------------------------
        varint_ = read_raw_b64(chan)
        offset3 = chan.position
        self.assertEqual(nnn, varint_)
        self.assertEqual(offset2 + 8, offset3)

    def test_encode_decode(self):
        self.round_trip32(0)
        self.round_trip32(42)
        self.round_trip32(0x7f)
        self.round_trip32(0x80)
        self.round_trip32(0x3fff)
        self.round_trip32(0x4000)
        self.round_trip32(0x1fffff)
        self.round_trip32(0x200000)
        self.round_trip32(0xfffffff)
        self.round_trip32(0x10000000)
        self.round_trip32(0xffffffff)

        self.round_trip64(0)
        self.round_trip64(42)
        self.round_trip64(0x7f)
        self.round_trip64(0x80)
        self.round_trip64(0x3fff)
        self.round_trip64(0x4000)
        self.round_trip64(0x1fffff)
        self.round_trip64(0x200000)
        self.round_trip64(0xfffffff)
        self.round_trip64(0x10000000)
        self.round_trip64(0x7ffffffff)
        self.round_trip64(0x800000000)
        self.round_trip64(0x3ffffffffff)
        self.round_trip64(0x40000000000)
        self.round_trip64(0x1ffffffffffff)
        self.round_trip64(0x2000000000000)
        self.round_trip64(0xffffffffffffff)
        self.round_trip64(0x100000000000000)
        self.round_trip64(0x7fffffffffffffff)
        self.round_trip64(0x8000000000000000)
        self.round_trip64(0xffffffffffffffff)

if __name__ == '__main__':
    unittest.main()
