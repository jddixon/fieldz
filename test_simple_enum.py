#!/usr/bin/env python3

# test_simple_enum.py
import time
import unittest

from rnglib import SimpleRNG
import fieldz.enum_spec as QQQ


class TestSimpleEnum(unittest.TestCase):

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
    def test_simple_enum(self):
        self.assertEqual(0, QQQ.REQUIRED)

if __name__ == '__main__':
    unittest.main()
