#!/usr/bin/env python3

# testLenPlus.py
import time
import unittest

from rnglib import SimpleRNG
#from fieldz.chan import *
#from fieldz.raw import *

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
        print("buffer after writing lenPlus field: " + str(buf))
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
