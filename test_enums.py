#!/usr/bin/env python3
# test_enums.py


import time
import unittest

from rnglib import SimpleRNG
from fieldz.enum import Quants

# DEPRECATED --------------------------------------------------------
from fieldz.enum import SimpleEnumWithRepr
import fieldz.enum_spec as QQQ
# END DEPRECATED ----------------------------------------------------


class TestEnums(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # DEPRECATED ----------------------------------------------------
    def test_simple_enum_with_repr(self):
        """ Tests DEPRECATED class. """

        self.assertEqual(0, QQQ.REQUIRED)
        self.assertEqual(1, QQQ.OPTIONAL)
        self.assertEqual(2, QQQ.STAR)
        self.assertEqual(3, QQQ.PLUS)

        simple = SimpleEnumWithRepr([('REQUIRED', ''),
                                     ('OPTIONAL', '?'),
                                     ('STAR', '*'),
                                     ('PLUS', '+')])

        self.assertEqual(simple.as_str(QQQ.REQUIRED), '')
        self.assertEqual(simple.as_str(QQQ.OPTIONAL), '?')
        self.assertEqual(simple.as_str(QQQ.STAR), '*')
        self.assertEqual(simple.as_str(QQQ.PLUS), '+')

    # END DEPRECATED ------------------------------------------------

    def test_quants(self):
        """ Verify that the sym() function works as expected. """
        self.assertEqual(Quants.sym(Quants.REQUIRED), '')
        self.assertEqual(Quants.sym(Quants.OPTIONAL), '?')
        self.assertEqual(Quants.sym(Quants.STAR), '*')
        self.assertEqual(Quants.sym(Quants.PLUS), '+')

if __name__ == '__main__':
    unittest.main()
