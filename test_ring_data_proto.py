#!/usr/bin/env python3

# testRingDataProto.py

import binascii
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from ring_data_proto import RING_DATA_PROTO_SPEC

from fieldz.parser import StringProtoSpecParser
import fieldz.field_types as F
import fieldz.msg_spec as M
import fieldz.typed as T
from xlattice.node import Node
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class

RNG = SimpleRNG(int(time.time()))
BUFSIZE = 16 * 1024
HOST_BY_NAME = {}
HOST_BY_ADDR = {}
HOST_BY_NODE_ID = {}
HOST_BY_PUB_KEY = {}
HOST_BY_PRIVATE_KEYE = {}


class HostInfo(object):
    __slots__ = ['_name', '_ipAddr', '_nodeID', '_pubKey',
                 '_privateKey', ]

    def __init__(self, name=None, ipAddr=None, node_id=None,
                 pub_key=None, priv_key=None):
        self._name = name
        self._ipAddr = ipAddr
        self._nodeID = node_id
        self._pubKey = pub_key
        self._privateKey = priv_key

    @classmethod
    def createRandomHost(cls):
        name, dottedQ, node_id, pub_key, priv_key = hostInfoValues()
        return cls(name, dottedQ, node_id, pub_key, priv_key)


class RingData(object):
    __slots__ = ['_hosts', ]

    def __init__(self, hosts):
        # DEBUG
        # END
        self._hosts = []
        for h in hosts:
            self._hosts.append(h)

    @classmethod
    def createRandomRing(cls):
        ring = ringDataValues()
        return cls(ring)


def ringDataValues():
    count = 2 + RNG.next_int16(4)    # so 2 to 5 hosts
    ring = []
    for nnn in range(count):
        host = HostInfo.createRandomHost()
        ring.append(host)
    # DEBUG
    print("RING_DATA_VALUES returning a list of %u hosts" % len(ring))
    # END
    return ring


def hostInfoValues():
    max_count = 8
    nnn = 0
    while nnn < max_count:
        nnn = nnn + 1
        node = Node()  # by default uses SHA3 and generates RSA keys
        priv_key = node.key.exportKey()
        pub_key = node.pub_key.exportKey()
        hexNodeID = binascii.b2a_hex(node.node_id)

#       # DEBUG
#       print "PRIVATE KEY: " + str(privateKey)
#       print "PUBLIC KEY:  " + repr(pubKey)
#       # END

        name = RNG.next_file_name(8)

        addr = RNG.next_int32()
        dottedQ = '%d.%d.%d.%d' % (
            (addr >> 24 & 0xff),
            (addr >> 16 & 0xff),
            (addr >> 8 & 0xff),
            (addr & 0xff))
        # DEBUG
        print("name is      '%s'" % name)
        print("addr is      '%s'" % addr)
        print("dottedQ is   '%s'" % dottedQ)
        print("hexNodeID is '%s'\n" % hexNodeID)
        # END
        if name in HOST_BY_NAME:
            continue
        if dottedQ in HOST_BY_ADDR:
            continue
        if hexNodeID in HOST_BY_NODE_ID:       # hex value
            continue
        # DEBUG
        # print "PUB_KEY: %s" % pubKey.n
        # END
        if pub_key in HOST_BY_PUB_KEY:
            print("pubKey is not unique")
            continue
        if priv_key in HOST_BY_PRIVATE_KEYE:
            print("privateKey is not unique")
            continue

        # we require that all of these fields be unique in the sample set
        HOST_BY_NAME[name] = name      # dumb, but life is short
        HOST_BY_ADDR[dottedQ] = name
        HOST_BY_NODE_ID[hexNodeID] = name
        HOST_BY_PUB_KEY[pub_key] = name
        HOST_BY_PRIVATE_KEYE[priv_key] = name

        # NOTE that nodeID is a binary value here
        return (name, dottedQ, node.node_id, pub_key, priv_key)  # GEEP


class TestRingDataProto(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################

    def dump_buffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    def make_str_obj_model(self):
        # MODEL: testProtoSpec XXX
        data = StringIO(RING_DATA_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)
        str_obj_model = ppp.parse()             # object model from string serialization
        return str_obj_model

    # actual unit tests #############################################
    def test_ring_data_proto(self):
        str_obj_model = self.make_str_obj_model()
        self.assertIsNotNone(str_obj_model)
        self.assertTrue(isinstance(str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.pzog.ringData', str_obj_model.name)
        self.assertEqual(0, len(str_obj_model.enums))
        self.assertEqual(1, len(str_obj_model.msgs))
        self.assertEqual(0, len(str_obj_model.seqs))

        # OUTER MESSAGE SPEC ----------------------------------------
        msg_spec = str_obj_model.msgs[0]
        field = msg_spec[0]
        self.assertEqual(field._name, 'hosts')
        self.assertEqual(field.field_type_name, 'hostInfo')
        self.assertEqual(field.quantifier, M.Q_PLUS)

        # INNER MESSAGE SPEC ----------------------------------------
        msg_spec = str_obj_model.msgs[0].msgs[0]
        self.assertEqual(msg_spec.f_name(0), 'hostName')
        self.assertEqual(msg_spec.field_type_name(0), 'lstring')
        self.assertEqual(msg_spec.f_name(1), 'ipAddr')
        self.assertEqual(msg_spec.field_type_name(1), 'lstring')
        self.assertEqual(msg_spec.f_name(2), 'node_id')
        self.assertEqual(msg_spec.field_type_name(2), 'fbytes32')
        self.assertEqual(msg_spec.f_name(3), 'pub_key')
        self.assertEqual(msg_spec.field_type_name(3), 'lstring')
        self.assertEqual(msg_spec.f_name(4), 'priv_key')
        self.assertEqual(msg_spec.field_type_name(4), 'lstring')
        try:
            msg_spec.f_name(5)
            self.fail('did not catch reference to non-existent field')
        except IndexError as i_exc:
            pass                                                    # GEEP

    # ---------------------------------------------------------------
    def test_caching(self):
        """ verify that classes with the same definition are cached """
        str_obj_model = self.make_str_obj_model()
        proto_name = str_obj_model.name
        self.assertTrue(isinstance(str_obj_model, M.ProtoSpec))

        outer_msg_spec = str_obj_model.msgs[0]
        inner_msg_spec = str_obj_model.msgs[0].msgs[0]
        OuterMsg = make_msg_class(str_obj_model, outer_msg_spec.name)
        # NOTE change in parent
        InnerMsg = make_msg_class(outer_msg_spec, inner_msg_spec.name)

        # TEST INNER MESSAGE ########################################
        Clz0 = make_msg_class(outer_msg_spec, inner_msg_spec.name)
        Clz1 = make_msg_class(outer_msg_spec, inner_msg_spec.name)
        # we cache classes, so the two should be the same
        self.assertEqual(id(Clz0), id(Clz1))

        # test that msg instances created from the same value lists differ
        values = hostInfoValues()
        inner_msg0 = Clz0(values)
        inner_msg1 = Clz0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(inner_msg0), id(inner_msg1))

        # verify that field classes are cached
        field_spec = inner_msg_spec[0]
        dotted_name = '%s.%s' % (proto_name, inner_msg_spec.name)
        F0 = make_field_class(dotted_name, field_spec)
        F1 = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(F0), id(F1))           # GEEP

        # TEST OUTER MESSAGE ########################################
        Clz2 = make_msg_class(str_obj_model, outer_msg_spec.name)
        Clz3 = make_msg_class(str_obj_model, outer_msg_spec.name)
        # we cache classe, so the two should be the same
        self.assertEqual(id(Clz2), id(Clz3))

        # test that msg instances created from the same value lists differ
        ring = ringDataValues()  # a list of random hosts

        # 'values' is a list of field values.  In this case, the single
        # value is itself a list, a list of HostInfo value lists.
        values = [ring]            # a list whose only member is a list

        outer_msg0 = Clz2(values)
        outer_msg1 = Clz2(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(outer_msg0), id(outer_msg1))

        field_spec = outer_msg_spec[0]
        dotted_name = '%s.%s' % (proto_name, outer_msg_spec.name)
        F0 = make_field_class(dotted_name, field_spec)
        F1 = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(F0), id(F1))           # GEEP

    # ---------------------------------------------------------------
    def testRingDataProtoSerialization(self):
        str_obj_model = self.make_str_obj_model()
        proto_name = str_obj_model.name
        outer_msg_spec = str_obj_model.msgs[0]
        inner_msg_spec = str_obj_model.msgs[0].msgs[0]
        OuterMsg = make_msg_class(str_obj_model, outer_msg_spec.name)
        # NOTE change in parent
        InnerMsg = make_msg_class(outer_msg_spec, inner_msg_spec.name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create a message instance ---------------------------------

        # create some HostInfo instances
        count = 2 + RNG.next_int16(7)  # so 2 .. 8
        ring = []
        for nnn in range(count):
            # should avoid dupes
            values = hostInfoValues()
            ring.append(InnerMsg(values))

        outerMsg = OuterMsg([ring])     # a list whose member is a list

        # serialize the object to the channel -----------------------
        nnn = outerMsg.write_stand_alone(chan)

        old_position = chan.position
        chan.flip()
        self.assertEqual(old_position, chan.limit)
        self.assertEqual(0, chan.position)

        # deserialize the channel, making a clone of the message ----
        (read_back, nn2) = OuterMsg.read(chan, str_obj_model)
        self.assertIsNotNone(read_back)

        # verify that the messages are identical --------------------
        self.assertTrue(outerMsg.__eq__(read_back))
        self.assertEqual(nnn, nn2)

        # produce another message from the same values --------------
        outerMsg2 = OuterMsg([ring])
        chan2 = Channel(BUFSIZE)
        nnn = outerMsg2.write_stand_alone(chan2)
        chan2.flip()
        (copy2, nn3) = OuterMsg.read(chan2, str_obj_model)
        self.assertTrue(outerMsg.__eq__(copy2))
        self.assertTrue(outerMsg2.__eq__(copy2))                   # GEEP

    # ---------------------------------------------------------------
    def roundTripRingDataInstanceToWireFormat(self, spec, ringHost):

        # invoke WireMsgSpecWriter
        # XXX STUB

        # invoke WireMsgSpecParser
        # XXX STUB

        pass

    def test_round_trip_ring_data_instances_to_wire_format(self):
        strSpec = StringIO(RING_DATA_PROTO_SPEC)
        ppp = StringProtoSpecParser(strSpec)
        ringDataSpec = ppp.parse()

        count = 3 + RNG.next_int16(6)   # so 3..8 inclusive

        # make that many semi-random nodes, taking care to avoid duplicates,
        # and round-trip each
        for _ in range(count):
            ring_host = HostInfo.createRandomHost()
            self.roundTripRingDataInstanceToWireFormat(ringDataSpec, ring_host)


if __name__ == '__main__':
    unittest.main()
