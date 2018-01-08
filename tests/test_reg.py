#!/usr/bin/env python3

# test_reg.py
# import time
import unittest

# from rnglib import SimpleRNG
from wireops.enum import FieldTypes
from fieldz.reg import NodeReg
from fieldz.enum import CoreTypes

# TESTS --------------------------------------------------------------


class TestReg(unittest.TestCase):

    def test_node_reg(self):

        test_reg = NodeReg()

        nbr_coretypes = len(CoreTypes)
        self.assertEqual(nbr_coretypes, 6)
        nbr_fieldtypes = len(FieldTypes)
        self.assertEqual(nbr_fieldtypes, 18)

        # DEBUG
        print("test_node_reg: nbr_coretypes is %d" % nbr_coretypes)
        print("test_node_reg: nbr_fieldtypes is %d" % nbr_fieldtypes)
        print(
            "test_node_reg: test_reg.next_reg_id is %d test_reg.next_reg_id" %
            test_reg.next_reg_id)
        # END
        self.assertEqual(
            len(FieldTypes) + nbr_coretypes,
            test_reg.next_reg_id)

        # verify that all fieldTypes are defined in the registry, each
        # with the proper index (vBool through fBytes32 at FieldTypes.MAX_NDX)
        for ndx, ftype in enumerate(FieldTypes):
            name = test_reg[ndx].qual_name
            # DEBUG
            print('%2u %s' % (ndx, name))
            # END
            self.assertEqual(ftype.sym, name)

        for ndx, coretype in enumerate(CoreTypes):
            i = ndx + nbr_fieldtypes
            name = test_reg[i].qual_name
            # DEBUG
            print('%2u %s' % (i, name))
            # END
            self.assertEqual(coretype.sym, name)
            # XXX FIGURE THIS OUT
            # self.assertEqual(test_reg.name2reg_id(name), i)

        self.assertEqual(nbr_fieldtypes + nbr_coretypes, len(test_reg))

#       print "DEBUG: len(test_reg) is %u" % len(test_reg)
#       print "DEBUG: next_reg_id is %u"    % test_reg.next_reg_id

        self.assertEqual(len(test_reg), test_reg.next_reg_id)


if __name__ == '__main__':
    unittest.main()
