#!/usr/bin/env python3

# testBigTest.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
# from fieldz.msg_spec import *
from fieldz.msg_spec import Q_REQUIRED  # , Q_OPTIONAL, Q_PLUS, Q_STAR
from fieldz.parser import StringProtoSpecParser

import fieldz.enum_spec as QQQ
import fieldz.reg as R

from big_test import BIG_TEST


class TestBigTest (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def round_trip_poto_spec_via_string(self, match):
        """
        Convert a ProtoSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        equal.
        """
        canonical_spec = match.__repr__()
        # DEBUG
        #print("CANONICAL SPEC:\n" + canonicalSpec)
        # END
        ppp = StringProtoSpecParser(StringIO(canonical_spec))
        cloned_spec = ppp.parse()
        # crude tests of __eq__ AKA ==
        self.assertFalse(match is None)
        self.assertTrue(match == match)

        # one way of saying it ------------------
        self.assertTrue(match.__eq__(cloned_spec))
        self.assertTrue(cloned_spec.__eq__(match))
        # this is the same test -----------------
        self.assertTrue(match == cloned_spec)
        self.assertTrue(cloned_spec == match)

    def testCompiler(self):
        node_reg = R.NodeReg()
        protocol = 'org.xlattice.fieldz.test.bigProto'
        proto_reg = R.ProtoReg(protocol, node_reg)

        data = StringIO(BIG_TEST)
        self.assertIsNotNone(data)
        ppp = StringProtoSpecParser(data)
        bigProtoSpec = ppp.parse()

        # confirm that field numbers are unique and increasing
        match = bigProtoSpec.msgs[0]
        lastFieldNbr = -1
        for field in match:
            self.assertTrue(field.field_nbr > lastFieldNbr)
            lastFieldNbr = field.field_nbr

        self.round_trip_poto_spec_via_string(bigProtoSpec)

    # ---------------------------------------------------------------
    def roundTripProtoInstanceToWireFormat(self, match):

        # invoke WireMsgSpecWriter
        # XXX STUB

        # invoke WireMsgSpecParser
        # XXX STUB

        pass

    # XXX IN EFFECT COMMENTED OUT XXX
    def XtestRoundTripBigTestInstancesToWireFormat(self):
        # strSpec = StringIO(BIG_TEST)
        strSpec = StringIO(BIG_TEST)
        ppp = StringProtoSpecParser(strSpec)
        bigMsgSpec = ppp.parse()

        self.roundTripProtoInstanceToWireFormat(bigMsgSpec)


if __name__ == '__main__':
    unittest.main()
