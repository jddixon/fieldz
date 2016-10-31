#!/usr/bin/env python3

# test_reg.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.reg import NodeReg
from fieldz.core_types import CoreTypes
from fieldz.field_types import FieldTypes, FieldStr

# TESTS --------------------------------------------------------------


class TestReg(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def test_node_reg(self):
        c_types = CoreTypes()
        test_reg = NodeReg()

        # bootstrap() has loaded fieldTypes and coreTypes
#       print "DEBUG: FieldTypes.MAX_NDX is %d" % FieldTypes.MAX_NDX        # is 17
#       print "DEBUG: C.maxNdx is %d" % C.maxNdx        # is  5
#       print "DEBUG: test_reg.nextRegID is %d test_reg.nextRegID
        self.assertEqual(
            FieldTypes.MAX_NDX +
            1 +
            c_types.max_ndx +
            1,
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

        for i in range(FieldTypes.MAX_NDX + 1,
                       FieldTypes.MAX_NDX + 1 + c_types.max_ndx + 1):
            name = test_reg[i].qual_name
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(c_types.as_str(
                i - (FieldTypes.MAX_NDX + 1)), name)
            self.assertEqual(i, test_reg.name2reg_id(name))

        # F and C range from 0 to maxNdx
        self.assertEqual(
            FieldTypes.MAX_NDX +
            1 +
            c_types.max_ndx +
            1,
            len(test_reg))

#       print "DEBUG: len(test_reg) is %u" % len(test_reg)
#       print "DEBUG: nextRegID is %u"    % test_reg.nextRegID

        self.assertEqual(len(test_reg), test_reg.next_reg_id)


if __name__ == '__main__':
    unittest.main()
