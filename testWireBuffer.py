#!/usr/bin/python3

# testWireBuffer.py
import time, unittest

from rnglib import SimpleRNG
from fieldz.raw import *

class TestWireBuffer (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # actual unit tests #############################################
   
    def testPowersOfTwo(self):
        self.assertRaises(ValueError, nextPowerOfTwo, -1)
        self.assertRaises(ValueError, nextPowerOfTwo, 0)
        self.assertEqual(16, nextPowerOfTwo(15))
        self.assertEqual(16, nextPowerOfTwo(16))

    def testWireBuffer(self):

        wb = WireBuffer(1023)  
        self.assertEqual(1024,         wb.capacity)
        self.assertEqual(0,            wb.position)
        self.assertEqual(0,            wb.buffer[0])
        self.assertEqual(wb.capacity,  len(wb.buffer))

        try:
            wb.position = wb.capacity
            self.fail('positioned beyond end of buffer')
        except ValueError:
            pass
        wb.position = wb.capacity - 10  # position near end
        wb.reserve(16)                  # will exceed capacity
        # so the buffer size doubles ...
        self.assertEqual(2 * 1024, wb.capacity)

    def testCopy(self):
        wb  = WireBuffer(4095)
        self.assertEqual(4096, wb.capacity)
        wb.position = 27
        self.assertEqual(27,   wb.position)

        wb2 = wb.copy()
        self.assertEqual(4096, wb2.capacity)
        self.assertEqual(0,    wb2.position)

        self.assertEqual(wb.buffer, wb2.buffer)

if __name__ == '__main__':
    unittest.main()
