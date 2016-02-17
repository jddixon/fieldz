#!/usr/bin/python

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
        self.assertEquals(16, nextPowerOfTwo(15))
        self.assertEquals(16, nextPowerOfTwo(16))

    def testWireBuffer(self):

        wb = WireBuffer(1023)  
        self.assertEquals(1024,         wb.capacity)
        self.assertEquals(0,            wb.position)
        self.assertEquals(0,            wb.buffer[0])
        self.assertEquals(wb.capacity,  len(wb.buffer))

        try:
            wb.position = wb.capacity
            self.fail('positioned beyond end of buffer')
        except ValueError:
            pass
        wb.position = wb.capacity - 10  # position near end
        wb.reserve(16)                  # will exceed capacity
        # so the buffer size doubles ...
        self.assertEquals(2 * 1024, wb.capacity)

    def testCopy(self):
        wb  = WireBuffer(4095)
        self.assertEquals(4096, wb.capacity)
        wb.position = 27
        self.assertEquals(27,   wb.position)

        wb2 = wb.copy()
        self.assertEquals(4096, wb2.capacity)
        self.assertEquals(0,    wb2.position)

        self.assertEquals(wb.buffer, wb2.buffer)

if __name__ == '__main__':
    unittest.main()
