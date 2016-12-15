#!/usr/bin/env python3

# test_wire_buffer.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.raw import(
    next_power_of_two,
    WireBuffer,
)
# from fieldz.raw import *


class TestWireBuffer (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # actual unit tests #############################################

    def test_pow(self):
        self.assertRaises(ValueError, next_power_of_two, -1)
        self.assertRaises(ValueError, next_power_of_two, 0)
        self.assertEqual(16, next_power_of_two(15))
        self.assertEqual(16, next_power_of_two(16))

    def test_wire_buffer(self):

        wb_ = WireBuffer(1023)
        self.assertEqual(1024, wb_.capacity)
        self.assertEqual(0, wb_.position)
        self.assertEqual(0, wb_.buffer[0])
        self.assertEqual(wb_.capacity, len(wb_.buffer))

        try:
            wb_.position = wb_.capacity
            self.fail('positioned beyond end of buffer')
        except ValueError:
            pass
        wb_.position = wb_.capacity - 10  # position near end
        wb_.reserve(16)                  # will exceed capacity
        # so the buffer size doubles ...
        self.assertEqual(2 * 1024, wb_.capacity)

    def test_copy(self):
        wb_ = WireBuffer(4095)
        self.assertEqual(4096, wb_.capacity)
        wb_.position = 27
        self.assertEqual(27, wb_.position)

        wb_2 = wb_.copy()
        self.assertEqual(4096, wb_2.capacity)
        self.assertEqual(0, wb_2.position)

        self.assertEqual(wb_.buffer, wb_2.buffer)

if __name__ == '__main__':
    unittest.main()
