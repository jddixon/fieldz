#!/usr/bin/env python3

# testReg.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.reg import NodeReg
import fieldz.core_types as C
from fieldz.field_types import FieldTypes, FieldStr

# TESTS --------------------------------------------------------------


class TestReg (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def testNodeReg(self):
        testReg = NodeReg()

        # bootstrap() has loaded fieldTypes and coreTypes
#       print "DEBUG: FieldTypes.MAX_NDX is %d" % FieldTypes.MAX_NDX        # is 17
#       print "DEBUG: C.maxNdx is %d" % C.maxNdx        # is  5
#       print "DEBUG: testReg.nextRegID is %d" % testReg.nextRegID
        self.assertEqual(
            FieldTypes.MAX_NDX +
            1 +
            C.CoreTypes().max_ndx +
            1,
            testReg.next_reg_id)

        # verify that all fieldTypes are defined in the registry, each
        # with the proper index (vBool through fBytes32 at FieldTypes.MAX_NDX)
        C_TYPES = C.CoreTypes()
        for i in range(FieldTypes.MAX_NDX + 1):
            name = testReg[i].qual_name
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(FieldStr.as_str(i), name)
            self.assertEqual(i, testReg.name2reg_id(name))

        for i in range(FieldTypes.MAX_NDX + 1,
                       FieldTypes.MAX_NDX + 1 + C_TYPES.max_ndx + 1):
            name = testReg[i].qual_name
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(C_TYPES.as_str(
                i - (FieldTypes.MAX_NDX + 1)), name)
            self.assertEqual(i, testReg.name2reg_id(name))

        # F and C range from 0 to maxNdx
        self.assertEqual(
            FieldTypes.MAX_NDX +
            1 +
            C_TYPES.max_ndx +
            1,
            len(testReg))

#       print "DEBUG: len(testReg) is %u" % len(testReg)
#       print "DEBUG: nextRegID is %u"    % testReg.nextRegID

        self.assertEqual(len(testReg), testReg.next_reg_id)


if __name__ == '__main__':
    unittest.main()
