#!/usr/bin/env python3

# testLenPlus.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.chan import *
from fieldz.raw import *

LEN_BUFF = 1024


class TestLenPlus (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def dumpBuffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    def roundTrip(self, s):
        """
        this tests writing and reading a string of bytes as the first and
        only field in a buffer
        """
        chan = Channel(LEN_BUFF)
        buf = chan.buffer

        # -- write the bytearray ------------------------------------
        fieldNbr = 1 + self.rng.nextInt16(1024)
        writeLenPlusField(chan, s, fieldNbr)
        chan.flip()

#       # DEBUG
        print("buffer after writing lenPlus field: " + str(buf))
#       # END

        # -- read the value written ---------------------------------
        # first the header (which is a varint) ------------
        (fieldType, fieldNbr2,) = readFieldHdr(chan)
        offset2 = chan.position
        self.assertEqual(LEN_PLUS_TYPE, fieldType)
        self.assertEqual(fieldNbr, fieldNbr2)
        self.assertEqual(lengthAsVarint(fieldHdr(fieldNbr, LEN_PLUS_TYPE)),
                         offset2)

        # then the actual value written -------------------
        t = readRawLenPlus(chan)
        offset3 = chan.position
        self.assertEqual(s, t)
        self.assertEqual(offset2 + lengthAsVarint(len(s)) + len(s), offset3)

    def testEncodeDecode(self):
        self.roundTrip('')
        self.roundTrip('x')
        self.roundTrip('should be a random string of bytes')

if __name__ == '__main__':
    unittest.main()
