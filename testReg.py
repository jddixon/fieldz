#!/usr/bin/python

# testReg.py
import time, unittest

from rnglib         import SimpleRNG
from fieldz.reg     import NodeReg
import fieldz.fieldTypes as F
import fieldz.coreTypes  as C

# TESTS --------------------------------------------------------------
class TestReg (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################


    # actual unit tests #############################################
    def testNodeReg(self):
        testReg = NodeReg()

        # bootstrap() has loaded fieldTypes and coreTypes
#       print "DEBUG: F.maxNdx is %d" % F.maxNdx        # is 17
#       print "DEBUG: C.maxNdx is %d" % C.maxNdx        # is  5
#       print "DEBUG: testReg.nextRegID is %d" % testReg.nextRegID
        self.assertEquals( F.maxNdx + 1 + C.maxNdx + 1, testReg.nextRegID )

        # verify that all fieldTypes are defined in the registry, each
        # with the proper index (vBool through fBytes32 at F.maxNdx)
        for i in range(F.maxNdx + 1):
            name = testReg[i].qualName
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEquals(F.asStr(i), name)
            self.assertEquals(i, testReg.name2RegID(name))

        for i in range(F.maxNdx + 1, F.maxNdx + 1 + C.maxNdx + 1):
            name = testReg[i].qualName
            # DEBUG
#           print '%2u %s' % (i, name)
            # END
            self.assertEquals(C.asStr(i - (F.maxNdx + 1)), name)
            self.assertEquals(i, testReg.name2RegID(name))
      
        # F and C range from 0 to maxNdx
        self.assertEquals( F.maxNdx + 1 + C.maxNdx + 1, len(testReg))

#       print "DEBUG: len(testReg) is %u" % len(testReg)
#       print "DEBUG: nextRegID is %u"    % testReg.nextRegID

        self.assertEquals( len(testReg), testReg.nextRegID )


if __name__ == '__main__':
    unittest.main()
