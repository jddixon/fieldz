#!/usr/bin/env python3

# testReg.py
import time
import unittest

from rnglib import SimpleRNG
from fieldz.reg import NodeReg
import fieldz.core_types as C
from fieldz.field_types import FieldTypes as F, FieldStr as FS

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
#       print "DEBUG: F.MAX_NDX is %d" % F.MAX_NDX        # is 17
#       print "DEBUG: C.maxNdx is %d" % C.maxNdx        # is  5
#       print "DEBUG: testReg.nextRegID is %d" % testReg.nextRegID
        self.assertEqual(
            F.MAX_NDX +
            1 +
            C.CoreTypes().maxNdx +
            1,
            testReg.nextRegID)

        # verify that all fieldTypes are defined in the registry, each
        # with the proper index (vBool through fBytes32 at F.MAX_NDX)
        fs = FS()
        cTypes = C.CoreTypes()
        for i in range(F.MAX_NDX + 1):
            name = testReg[i].qualName
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(fs.asStr(i), name)
            self.assertEqual(i, testReg.name2RegID(name))

        for i in range(F.MAX_NDX + 1, F.MAX_NDX + 1 + cTypes.maxNdx + 1):
            name = testReg[i].qualName
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEqual(cTypes.asStr(i - (F.MAX_NDX + 1)), name)
            self.assertEqual(i, testReg.name2RegID(name))

        # F and C range from 0 to maxNdx
        self.assertEqual(F.MAX_NDX + 1 + cTypes.maxNdx + 1, len(testReg))

#       print "DEBUG: len(testReg) is %u" % len(testReg)
#       print "DEBUG: nextRegID is %u"    % testReg.nextRegID

        self.assertEqual(len(testReg), testReg.nextRegID)


if __name__ == '__main__':
    unittest.main()
