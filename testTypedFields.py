#!/usr/bin/env python3

# testTypedFields.py

import ctypes                   # a bit of desperation here
import sys
import time
import unittest

from rnglib import SimpleRNG
from fieldz.raw import *
from fieldz.fieldTypes import FieldTypes as F, FieldStr as FS

LEN_NULLS = 1024
NULLS = [0] * LEN_NULLS

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXX BEING DROPPED.  ANYTHING OF VALUE SHOULD GO INTO testTFWriter
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TestTypedFields (unittest.TestCase):

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
    def roundTripList(self, triplets):
        """
        Given a list of name-type-value pairs, produce an encoding in a
        buffer; then decode the buffer to produce a second list of
        field number-type-value triplets.  Require that the lists are
        congruent.

        XXX THIS IS JUST WRONG.  We need two lists, one implementing
        the sspec and one implementing an sinst

        XXX NOW IT'S OBSOLETE TOO.
        """

        # remember field numbers are one-based XXX
        fs = FS()
        for f in triplets:
            print("field  %-7s: " % f[0], end=' ')
            print("type %2s = %-8s " % (f[1], fs.asStr(f[1])))

    def testEncodeDecode(self):
        # crude sanity check
        # OBSOLETE
        #       self.assertEqual( F._V_BOOL,   F._V_BOOL     )
        #       self.assertEqual( F._MAX_TYPE, F.fBytes32  )

        rng = self.rng
        buffer = [0] * (16 * LEN_NULLS)
        # for lBytes
        byteBuf = [0] * (1 + rng.nextInt16(16))
        byte20Buf = [0] * 20
        byte32Buf = [0] * 32

        fieldSpecs  = [ \
            # name,    type,       value
            ('inVino', F._V_BOOL, rng.nextBoolean()),

            # An enumeration has associated with it a list of names,
            # and that list has a length.  The field value is
            # restricted to 0..len
            ('nummer', F._V_ENUM, rng.nextInt16(7)),

            # simple varints; half will be negative and so very long
            ('i32', F._V_INT32, rng.nextInt32() - (65536 * 65536)),
            ('i64',     F._V_INT64,   rng.nextInt64() \
             - 65536 * 65536 * 65536 * 65536),
            # these are zig-zag encoded, optimal for small absolute values
            ('si32', F._V_SINT32, rng.nextInt32() - (65536 * 65536)),
            ('si64',    F._V_SINT64,   rng.nextInt64() \
             - 65536 * 65536 * 65536 * 65536),
            # unsigned, we hope
            ('ui32', F._V_UINT32, rng.nextInt32()),
            ('ui64', F._V_UINT64, rng.nextInt64()),
            # fixed length
            ('fi32', F._F_UINT32, rng.nextInt32() - (65536 * 65536)),
            ('fi64',    F._F_UINT64,   rng.nextInt64() \
             - 65536 * 65536 * 65536 * 65536),

            # XXX rnglib deficiency, or is it a Python deficiency?
            # These is no such thing as a four-byte float :-(
            # A Python float is a double.  We hack:
            ('freal32', F._F_FLOAT, ctypes.c_float(rng.nextReal())),
            ('freal64', F._F_DOUBLE, rng.nextReal()),

            # number of characters is 1..16
            ('ls', F._L_STRING, rng.nextFileName(16)),
            ('lb', F._L_BYTES, rng.nextBytes(byteBuf)),
            ('fb20', F._F_BYTES20, rng.nextBytes(byte20Buf)),
            ('fb32', F._F_BYTES32, rng.nextBytes(byte32Buf)),
        ]
        self.roundTripList(fieldSpecs)

if __name__ == '__main__':
    unittest.main()
