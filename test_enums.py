#!/usr/bin/env python3
# test_enums.py

import unittest

from fieldz.enum import CoreTypes, Quants


class TestEnums (unittest.TestCase):
    """
    Test sym(N) which returns symbolic form of the quantifier.
    """

    def test_core_types(self):
        self.assertEqual(len(CoreTypes), 6)
        # trivial checks
        self.assertEqual(CoreTypes.ENUM_PAIR_SPEC.value, 'EnumPairSpec')
        self.assertEqual(CoreTypes.PROTO_SPEC.value, 'ProtoSpec')

    def test_quants(self):
        self.assertEqual(len(Quants), 4)

        self.assertEqual(Quants.REQUIRED.value, '')
        self.assertEqual(Quants.OPTIONAL.value, '?')
        self.assertEqual(Quants.STAR.value, '*')
        self.assertEqual(Quants.PLUS.value, '+')


if __name__ == '__main__':
    unittest.main()
