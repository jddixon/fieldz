#!/usr/bin/env python3

# testLenPlus.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.chan import Channel
from fieldz.raw import(
    # VARINT_TYPE,                            # PACKED_VARINT_TYPE,
    B32_TYPE, B64_TYPE, LEN_PLUS_TYPE,
    B128_TYPE, B160_TYPE, B256_TYPE,

    field_hdr, field_hdr_len,
    read_field_hdr,
    # hdr_field_nbr, hdr_type,
    length_as_varint,  # write_varint_field,
    read_raw_varint, write_raw_varint,
    read_raw_b32,           # write_b32_field,
    read_raw_b64,           # write_b64_field,
    read_raw_len_plus,      #
    write_len_plus_field,
    read_raw_b128,          # write_b128_field,
    read_raw_b160,          # write_b160_field,
    read_raw_b256,          # write_b256_field,
    # next_power_of_two,
    # WireBuffer,
)

LEN_BUFF = 1024


class TestLenPlus(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    def round_trip(self, string):
        """
        this tests writing and reading a string of bytes as the first and
        only field in a buffer
        """
        chan = Channel(LEN_BUFF)
        buf = chan.buffer

        # -- write the bytearray ------------------------------------
        field_nbr = 1 + self.rng.next_int16(1024)
        write_len_plus_field(chan, string, field_nbr)
        chan.flip()

#       # DEBUG
#       print("buffer after writing lenPlus field: " + str(buf))
#       # END

        # -- read the value written ---------------------------------
        # first the header (which is a varint) ------------
        (field_type, field_nbr2,) = read_field_hdr(chan)
        offset2 = chan.position
        self.assertEqual(LEN_PLUS_TYPE, field_type)
        self.assertEqual(field_nbr, field_nbr2)
        self.assertEqual(length_as_varint(field_hdr(field_nbr, LEN_PLUS_TYPE)),
                         offset2)

        # then the actual value written -------------------
        tstamp = read_raw_len_plus(chan)
        offset3 = chan.position
        self.assertEqual(string, tstamp)
        self.assertEqual(
            offset2 +
            length_as_varint(
                len(string)) +
            len(string),
            offset3)

    def test_encode_decode(self):
        self.round_trip(''.encode('utf8'))
        self.round_trip('ndx_'.encode('utf8'))
        self.round_trip('should be a random string of bytes'.encode('utf8'))

if __name__ == '__main__':
    unittest.main()
