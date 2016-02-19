#!/usr/bin/python3

# testFieldTypes.py
import time, unittest

from rnglib     import SimpleRNG
import fieldz.fieldTypes    as F
import fieldz.raw           as R
import fieldz.typed         as T

class TestFieldTypes (unittest.TestCase):
    """
    Actually tests the method used for instantiating and importing
    an instance of the FieldTypes class.
    """

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################

    def dumpBuffer (self, buf):
        for i in range(16):
            print("0x%02x " % buf[i])
        print()


    # actual unit tests #############################################
    def testConstants(self):
        self.assertEqual( 0, F._V_BOOL    )
        self.assertEqual(17, F._F_BYTES32 )
        try:
            F._V_BOOL = 47
        except RuntimeError as e:
            print('success: caught attempt to reassign constant')    # DEBUG
            pass

    def testLenFuncs(self):
        n = self.rng.nextInt16()        # random field number
        x = self.rng.nextInt16()        # random integer value

        # == varint types ===========================================
        h = R.fieldHdrLen(n, F._V_BOOL)
        self.assertEqual( h + 1, T.vBoolLen(True, n) )
        self.assertEqual( h + 1, T.vBoolLen(False, n) )

        h = R.fieldHdrLen(n, F._V_ENUM)
        z = h + R.lengthAsVarint(x)
        self.assertEqual( z, T.vEnumLen(x, n) )
        # self.assertEqual( x, T.vEnumLen(-x, n) )

        x = self.rng.nextInt32()
        self.assertTrue( x >= 0 )

        h = R.fieldHdrLen(n, F._V_UINT32)
        z = h + R.lengthAsVarint(x)
        self.assertEqual( z, T.vuInt32Len(x, n) )

        x = self.rng.nextInt32()
        self.assertTrue( x >= 0 )
        x = x - 0x80000000

        h = R.fieldHdrLen(n, F._V_SINT32)
        p = T.encodeSint32(x)
        z = h + R.lengthAsVarint(p)
        self.assertEqual( z, T.vsInt32Len(x, n) )

        x = self.rng.nextInt64()
        self.assertTrue( x >= 0 )

        h = R.fieldHdrLen(n, F._V_UINT64)
        z = h + R.lengthAsVarint(x)
        self.assertEqual( z, T.vuInt64Len(x, n) )

        x = self.rng.nextInt64()
        self.assertTrue( x >= 0 )
        x = x - 0x8000000000000000

        h = R.fieldHdrLen(n, F._V_SINT64)
        p = T.encodeSint64(x)
        z = h + R.lengthAsVarint(p)
        self.assertEqual( z, T.vsInt64Len(x, n) )  

        # == fixed length 4 byte ====================================
        x = self.rng.nextInt64()        # value should be ignored 

        self.assertTrue( x >= 0 )
        x = x - 0x8000000000000000

        # x is a signed 64 bit value whose value should be irrelevant
        h = R.fieldHdrLen(n, F._F_UINT32)
        self.assertEqual( h + 4, T.fuInt32Len(x, n) )

        h = R.fieldHdrLen(n, F._F_SINT32)
        self.assertEqual( h + 4, T.fsInt32Len(x, n) )

        h = R.fieldHdrLen(n, F._F_FLOAT)
        self.assertEqual( h + 4, T.fFloatLen(x, n) )

        # == fixed length 8 byte ====================================
        # n is that signed 64 bit value whose value should be irrelevant
        h = R.fieldHdrLen(n, F._F_UINT64)
        self.assertEqual( h + 8, T.fuInt64Len(x, n) )
        h = R.fieldHdrLen(n, F._F_SINT64)
        self.assertEqual( h + 8, T.fsInt64Len(x, n) )
        h = R.fieldHdrLen(n, F._F_DOUBLE)
        self.assertEqual( h + 8, T.fDoubleLen(x, n) )

        # == LEN PLUS types =========================================
        def doLenPlusTest(x, n):
            s = [0]*x
            k = len(s)
            h = R.fieldHdrLen(n, F._L_BYTES)
            expectedLen = h + R.lengthAsVarint(k) + k
            self.assertEqual( expectedLen, T.lBytesLen(s,n) )

        # -- lString ---------------------------------------
        s = self.rng.nextFileName(256)
        h = R.fieldHdrLen(n, F._L_STRING)
        k = len(s)
        expectedLen = h + R.lengthAsVarint(k) + k
        self.assertEqual(expectedLen, T.lStringLen(s, n))

        # -- lBytes ----------------------------------------
        doLenPlusTest(0x7f,     n)
        doLenPlusTest(0x80,     n)
        doLenPlusTest(0x3fff,   n)
        doLenPlusTest(0x4000,   n)

        # -- lMsg ------------------------------------------
        # XXX STUB

        # -- fixed length byte arrays -------------------------------
        buf = [0]*512       # length functions should ignore actual size

        h = R.fieldHdrLen(n, F._F_BYTES16)
        self.assertEqual( h + 16, T.fBytes16Len(buf, n) )
        
        h = R.fieldHdrLen(n, F._F_BYTES20)
        self.assertEqual( h + 20, T.fBytes20Len(buf, n) )
        
        h = R.fieldHdrLen(n, F._F_BYTES32)
        self.assertEqual( h + 32, T.fBytes32Len(buf, n) )

if __name__ == '__main__':
    unittest.main()
