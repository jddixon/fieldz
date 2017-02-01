#!/usr/bin/env python3
# test_enums.py


import time
import unittest

from rnglib import SimpleRNG

# DEPRECATED --------------------------------------------------------
from fieldz.enum import SimpleEnumWithRepr
from fieldz import enum_spec
# END DEPRECATED ----------------------------------------------------


class TestEnums(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # DEPRECATED ----------------------------------------------------
    def test_simple_enum_with_repr(self):
        """ Tests DEPRECATED class. """

        self.assertEqual(0, enum_spec.REQUIRED)
        self.assertEqual(1, enum_spec.OPTIONAL)
        self.assertEqual(2, enum_spec.STAR)
        self.assertEqual(3, enum_spec.PLUS)

        simple = SimpleEnumWithRepr([('REQUIRED', ''),
                                     ('OPTIONAL', '?'),
                                     ('STAR', '*'),
                                     ('PLUS', '+')])

        self.assertEqual(simple.as_str(enum_spec.REQUIRED), '')
        self.assertEqual(simple.as_str(enum_spec.OPTIONAL), '?')
        self.assertEqual(simple.as_str(enum_spec.STAR), '*')
        self.assertEqual(simple.as_str(enum_spec.PLUS), '+')

    # END DEPRECATED ------------------------------------------------


if __name__ == '__main__':
    unittest.main()
