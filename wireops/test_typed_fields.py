#!/usr/bin/env python3

# testTypedFields.py

import ctypes                   # a bit of desperation here
# import sys
import time
import unittest

from rnglib import SimpleRNG
from fieldz.field_types import FieldTypes, FieldStr

LEN_NULLS = 1024
NULLS = [0] * LEN_NULLS

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXX BEING DROPPED.  ANYTHING OF VALUE SHOULD GO INTO testTFWriter
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


class TestTypedFields(unittest.TestCase):

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
    def round_trip_list(self, triplets):
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
        for file in triplets:
            print("field  %-7s: " % file[0], end=' ')
            print("type %2s = %-8s " % (file[1], FieldStr.as_str(file[1])))

    def test_encode_decode(self):
        # crude sanity check
        # OBSOLETE
        #       self.assertEqual( FieldTypes._V_BOOL,   FieldTypes._V_BOOL     )
        #       self.assertEqual( FieldTypes._MAX_TYPE, FieldTypes.fBytes32  )

        rng = self.rng
        buffer = [0] * (16 * LEN_NULLS)
        # for lBytes
        byte_buf = [0] * (1 + rng.next_int16(16))
        byte20buf = [0] * 20
        byte32buf = [0] * 32

        field_specs = [\
            # name,    type,       value
            ('inVino', FieldTypes.V_BOOL, rng.next_boolean()),

            # An enumeration has associated with it a list of names,
            # and that list has a length.  The field value is
            # restricted to 0..len
            ('nummer', FieldTypes.V_ENUM, rng.next_int16(7)),

            # simple varints; half will be negative and so very long
            ('i32', FieldTypes.V_INT32, rng.next_int32() - (65536 * 65536)),
            ('i64', FieldTypes.V_INT64, rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),
            # these are zig-zag encoded, optimal for small absolute values
            ('si32', FieldTypes.V_SINT32, rng.next_int32() - (65536 * 65536)),
            ('si64', FieldTypes.V_SINT64, rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),
            # unsigned, we hope
            ('ui32', FieldTypes.V_UINT32, rng.next_int32()),
            ('ui64', FieldTypes.V_UINT64, rng.next_int64()),
            # fixed length
            ('fi32', FieldTypes.F_UINT32, rng.next_int32() - (65536 * 65536)),
            ('fi64', FieldTypes.F_UINT64, rng.next_int64()\
             - 65536 * 65536 * 65536 * 65536),

            # XXX rnglib deficiency, or is it a Python deficiency?
            # These is no such thing as a four-byte float :-(
            # A Python float is a double.  We hack:
            ('freal32', FieldTypes.F_FLOAT, ctypes.c_float(rng.next_real())),
            ('freal64', FieldTypes.F_DOUBLE, rng.next_real()),

            # number of characters is 1..16
            ('ls', FieldTypes.L_STRING, rng.next_file_name(16)),
            ('lb', FieldTypes.L_BYTES, rng.next_bytes(byte_buf)),
            ('fb20', FieldTypes.F_BYTES20, rng.next_bytes(byte20buf)),
            ('fb32', FieldTypes.F_BYTES32, rng.next_bytes(byte32buf)),
        ]
        self.round_trip_list(field_specs)

if __name__ == '__main__':
    unittest.main()
