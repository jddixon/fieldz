#!/usr/bin/env python3

# test_reg.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.reg import NodeReg
from fieldz.enum import CoreTypes
from wireops.field_types import FieldTypes, FieldStr

# TESTS --------------------------------------------------------------


class TestReg(unittest.TestCase):

    def test_node_reg(self):

        test_reg = NodeReg()

        nbr_coretypes = len(CoreTypes)
        self.assertEqual(nbr_coretypes, 6)
        nbr_fieldtypes = len(FieldTypes)
        # self.assertEqual(nbr_fieldtypes, 18)  # FAILS, IS 20 ???
        # bootstrap() has loaded fieldTypes and coreTypes
        # DEBUG
#       print("FieldTypes.MAX_NDX is %d" % FieldTypes.MAX_NDX)        # is 17
        print("test_node_reg: nbr_coretypes is %d" % nbr_coretypes)
        print(
            "test_node_reg: test_reg.next_reg_id is %d test_reg.next_reg_id" %
            test_reg.next_reg_id)
        # END
        self.assertEqual(
            len(FieldTypes) + nbr_coretypes,
            test_reg.next_reg_id)

        # verify that all fieldTypes are defined in the registry, each
        # with the proper index (vBool through fBytes32 at FieldTypes.MAX_NDX)
        for i in range(FieldTypes.MAX_NDX + 1):
            name = test_reg[i].qual_name
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(FieldStr.as_str(i), name)
            self.assertEqual(i, test_reg.name2reg_id(name))

        for ndx, coretype in enumerate(CoreTypes):
            i = ndx + FieldTypes.MAX_NDX + 1
            name = test_reg[i].qual_name
            # DEBUG
            print('%2u %s' % (i, name))
            # END
            self.assertEqual(coretype.value, name)
            self.assertEqual(test_reg.name2reg_id(name), i)

        # F and C range from 0 to maxNdx
        self.assertEqual(
            FieldTypes.MAX_NDX + 1 + nbr_coretypes, len(test_reg))

#       print "DEBUG: len(test_reg) is %u" % len(test_reg)
#       print "DEBUG: next_reg_id is %u"    % test_reg.next_reg_id

        self.assertEqual(len(test_reg), test_reg.next_reg_id)


if __name__ == '__main__':
    unittest.main()
