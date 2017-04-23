#!/usr/bin/env python3
# test_enums.py

import unittest

from fieldz.enum import CoreTypes, Quants


class TestEnums(unittest.TestCase):
    """
    Test sym(N) which returns symbolic form of the quantifier.
    """

    def test_core_types(self):
        self.assertEqual(len(CoreTypes), 6)
        # trivial checks
        # pylint: disable=no-member
        self.assertEqual(CoreTypes.ENUM_PAIR_SPEC.sym, 'EnumPairSpec')
        self.assertEqual(CoreTypes.PROTO_SPEC.sym, 'ProtoSpec')

        self.assertEqual(len(CoreTypes), 6)

        # pylint: disable=not-an-iterable
        for _ in CoreTypes:
            self.assertEqual(CoreTypes.from_sym(_.sym), _)

    def test_quants(self):
        self.assertEqual(len(Quants), 4)

        # pylint: disable=no-member
        self.assertEqual(Quants.REQUIRED.sym, '')
        self.assertEqual(Quants.OPTIONAL.sym, '?')
        self.assertEqual(Quants.STAR.sym, '*')
        self.assertEqual(Quants.PLUS.sym, '+')

        self.assertEqual(len(Quants), 4)


if __name__ == '__main__':
    unittest.main()
