#!/usr/bin/python3

# testBigTest.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from fieldz.msgSpec import *
from fieldz.parser import StringProtoSpecParser

import fieldz.enumSpec as Q
import fieldz.reg as R

from bigTest import BIG_TEST


class TestBigTest (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def roundTripProtoSpecViaString(self, m):
        """
        Convert a ProtoSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """
        canonicalSpec = m.__repr__()
        # DEBUG
        #print("CANONICAL SPEC:\n" + canonicalSpec)
        # END
        p = StringProtoSpecParser(StringIO(canonicalSpec))
        clonedSpec = p.parse()
        # crude tests of __eq__ AKA ==
        self.assertFalse(m is None)
        self.assertTrue(m == m)

        # one way of saying it ------------------
        self.assertTrue(m.__eq__(clonedSpec))
        self.assertTrue(clonedSpec.__eq__(m))
        # this is the same test -----------------
        self.assertTrue(m == clonedSpec)
        self.assertTrue(clonedSpec == m)

    def testCompiler(self):
        nodeReg = R.NodeReg()
        protocol = 'org.xlattice.fieldz.test.bigProto'
        protoReg = R.ProtoReg(protocol, nodeReg)

        data = StringIO(BIG_TEST)
        p = StringProtoSpecParser(data)
        bigProtoSpec = p.parse()

        # confirm that field numbers are unique and increasing
        m = bigProtoSpec.msgs[0]
        lastFieldNbr = -1
        for field in m:
            self.assertTrue(field.fieldNbr > lastFieldNbr)
            lastFieldNbr = field.fieldNbr

        self.roundTripProtoSpecViaString(bigProtoSpec)

    # ---------------------------------------------------------------
    def roundTripProtoInstanceToWireFormat(self, m):

        # invoke WireMsgSpecWriter
        # XXX STUB

        # invoke WireMsgSpecParser
        # XXX STUB

        pass

    def testRoundTripBigTestInstancesToWireFormat(self):
        # strSpec = StringIO(BIG_TEST)
        strSpec = StringIO(BIG_TEST)
        p = StringProtoSpecParser(strSpec)
        bigMsgSpec = p.parse()

        self.roundTripProtoInstanceToWireFormat(bigMsgSpec)


if __name__ == '__main__':
    unittest.main()
