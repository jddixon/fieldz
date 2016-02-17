#!/usr/bin/python

# testTypedFields.py

import ctypes                   # a bit of desperation here
import sys, time, unittest

from rnglib         import SimpleRNG
from fieldz.raw     import *
import fieldz.fieldTypes as F

LEN_NULLS   = 1024
NULLS       = [0] * LEN_NULLS

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# XXX BEING DROPPED.  ANYTHING OF VALUE SHOULD GO INTO testTFWriter
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

class TestTypedFields (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################
    def dumpBuffer (self, buf):
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
        for f in triplets:
            print("field  %-7s: " % f[0], end=' ')
            print("type %2s = %-8s " % (f[1], F.repr(f[1])))

    def testEncodeDecode(self):
        # crude sanity check 
        # OBSOLETE
#       self.assertEquals( F._V_BOOL,   F.vBool     )
#       self.assertEquals( F._MAX_TYPE, F.fBytes32  )

        rng = self.rng
        buffer      = [0] * (16 * LEN_NULLS)
        # for lBytes
        byteBuf     = [0] * (1 + rng.nextInt16(16))
        byte20Buf   = [0] * 20
        byte32Buf   = [0] * 32

        fieldSpecs  = [ \
                  # name,    type,       value
                ('inVino',   F.vBool,    rng.nextBoolean() ),

                # An enumeration has associated with it a list of names,
                # and that list has a length.  The field value is 
                # restricted to 0..len
                ('nummer',   F.vEnum,   rng.nextInt16(7)),
                
                # simple varints; half will be negative and so very long
                ('i32',     F.vInt32,   rng.nextInt32() - (65536 * 65536)),
                ('i64',     F.vInt64,   rng.nextInt64() \
                                            - 65536*65536*65536*65536),
                # these are zig-zag encoded, optimal for small absolute values
                ('si32',    F.vsInt32,   rng.nextInt32() - (65536 * 65536)),
                ('si64',    F.vsInt64,   rng.nextInt64() \
                                            - 65536*65536*65536*65536),
                # unsigned, we hope
                ('ui32',    F.vuInt32,   rng.nextInt32()),
                ('ui64',    F.vuInt64,   rng.nextInt64()),
                # fixed length
                ('fi32',    F.fInt32,   rng.nextInt32() - (65536 * 65536)),
                ('fi64',    F.fInt64,   rng.nextInt64() \
                                            - 65536*65536*65536*65536),

                # XXX rnglib deficiency, or is it a Python deficiency?
                # These is no such thing as a four-byte float :-(
                # A Python float is a double.  We hack:
                ('freal32', F.fFloat,   ctypes.c_float(rng.nextReal())),
                ('freal64', F.fDouble,  rng.nextReal()),

                # number of characters is 1..16
                ('ls',      F.lString,  rng.nextFileName(16)),
                ('lb',      F.lBytes,   rng.nextBytes(byteBuf)),
                ('fb20',    F.fBytes20, rng.nextBytes(byte20Buf)),
                ('fb32',    F.fBytes32, rng.nextBytes(byte32Buf)),
        ]
        self.roundTripList(fieldSpecs)

if __name__ == '__main__':
    unittest.main()
