#!/usr/bin/env python3

# testBigTest.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from fieldz import reg
from fieldz.parser import StringProtoSpecParser

from big_test import BIG_TEST


class TestBigTest(unittest.TestCase):

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

    def test_compiler(self):
        node_reg = reg.NodeReg()
        protocol = 'org.xlattice.fieldz.test.bigProto'
        proto_reg = reg.ProtoReg(protocol, node_reg)

        data = StringIO(BIG_TEST)
        self.assertIsNotNone(data)
        ppp = StringProtoSpecParser(data)
        big_proto_spec = ppp.parse()

        # confirm that field numbers are unique and increasing
        match = big_proto_spec.msgs[0]
        last_field_nbr = -1
        for field in match:
            self.assertTrue(field.field_nbr > last_field_nbr)
            last_field_nbr = field.field_nbr

        self.round_trip_poto_spec_via_string(big_proto_spec)

    # ---------------------------------------------------------------
    def round_trip_proto_instance_to_wire_format(self, match):

        # invoke WireMsgSpecWriter
        # XXX STUB

        # invoke WireMsgSpecParser
        # XXX STUB

        pass

    # XXX EFFECTIVELY COMMENTED OUT XXX
    def x_test_round_trip_big_test_instances_to_wire_format(self):
        # str_spec = StringIO(BIG_TEST)
        str_spec = StringIO(BIG_TEST)
        ppp = StringProtoSpecParser(str_spec)
        big_msg_spec = ppp.parse()

        self.round_trip_proto_instance_to_wire_format(big_msg_spec)


if __name__ == '__main__':
    unittest.main()
