#!/usr/bin/env python3
# test_enums.py

""" Test enumerations defined in fieldz package. """

import unittest

from fieldz.enum import CoreTypes, Quants


class TestEnums(unittest.TestCase):
    """
    Test enumerations defined in fieldz package.
    """

    def test_core_types(self):
        """
        Test the CoreTypes enum, including sym and from_sym.
        """

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
        """ Test the Quants enum. """

        self.assertEqual(len(Quants), 4)

        # pylint: disable=no-member
        self.assertEqual(Quants.REQUIRED.sym, '')
        self.assertEqual(Quants.OPTIONAL.sym, '?')
        self.assertEqual(Quants.STAR.sym, '*')
        self.assertEqual(Quants.PLUS.sym, '+')

        self.assertEqual(len(Quants), 4)


if __name__ == '__main__':
    unittest.main()
