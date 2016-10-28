#!/usr/bin/env python3

# testTypedFields.py

import ctypes                   # a bit of desperation here
import sys
import time
import unittest

from rnglib import SimpleRNG
# from fieldz.raw import *
from fieldz.field_types import FieldTypes as F, FieldStr as FS

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
    def dump_buffer(self, buf):
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
        f_types = FS()
        for file in triplets:
            print("field  %-7s: " % file[0], end=' ')
            print("type %2s = %-8s " % (file[1], f_types.as_str(file[1])))

    def testEncodeDecode(self):
        # crude sanity check
        # OBSOLETE
        #       self.assertEqual( F._V_BOOL,   F._V_BOOL     )
        #       self.assertEqual( F._MAX_TYPE, F.fBytes32  )

        rng = self.rng
        buffer = [0] * (16 * LEN_NULLS)
        # for lBytes
        byte_buf = [0] * (1 + rng.next_int16(16))
        byte20Buf = [0] * 20
        byte32Buf = [0] * 32

        fieldSpecs  = [\
            # name,    type,       value
            ('inVino', F.V_BOOL, rng.next_boolean()),

            # An enumeration has associated with it a list of names,
            # and that list has a length.  The field value is
            # restricted to 0..len
            ('nummer', F.V_ENUM, rng.next_int16(7)),

            # simple varints; half will be negative and so very long
            ('i32', F.V_INT32, rng.next_int32() - (65536 * 65536)),
            ('i64',     F.V_INT64,   rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),
            # these are zig-zag encoded, optimal for small absolute values
            ('si32', F.V_SINT32, rng.next_int32() - (65536 * 65536)),
            ('si64',    F.V_SINT64,   rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),
            # unsigned, we hope
            ('ui32', F.V_UINT32, rng.next_int32()),
            ('ui64', F.V_UINT64, rng.next_int64()),
            # fixed length
            ('fi32', F.F_UINT32, rng.next_int32() - (65536 * 65536)),
            ('fi64',    F.F_UINT64,   rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),

            # XXX rnglib deficiency, or is it a Python deficiency?
            # These is no such thing as a four-byte float :-(
            # A Python float is a double.  We hack:
            ('freal32', F.F_FLOAT, ctypes.c_float(rng.next_real())),
            ('freal64', F.F_DOUBLE, rng.next_real()),

            # number of characters is 1..16
            ('ls', F.L_STRING, rng.next_file_name(16)),
            ('lb', F.L_BYTES, rng.next_bytes(byte_buf)),
            ('fb20', F.F_BYTES20, rng.next_bytes(byte20Buf)),
            ('fb32', F.F_BYTES32, rng.next_bytes(byte32Buf)),
        ]
        self.roundTripList(fieldSpecs)

if __name__ == '__main__':
    unittest.main()
