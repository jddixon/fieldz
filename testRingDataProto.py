#!/usr/bin/python3

# testRingDataProto.py

import binascii
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG
from ringDataProto import RING_DATA_PROTO_SPEC

from fieldz.parser import StringProtoSpecParser
import fieldz.fieldTypes as F
import fieldz.msgSpec as M
import fieldz.typed as T
from pzog.xlattice.node import Node
from fieldz.chan import Channel
from fieldz.msgImpl import makeMsgClass, makeFieldClass

rng = SimpleRNG(int(time.time()))
BUFSIZE = 16 * 1024
hostByName = {}
hostByAddr = {}
hostByNodeID = {}
hostByPubKey = {}
hostByPrivateKey = {}


class HostInfo(object):
    __slots__ = ['_name', '_ipAddr', '_nodeID', '_pubKey',
                 '_privateKey', ]

    def __init__(self, name=None, ipAddr=None, nodeID=None,
                 pubKey=None, privateKey=None):
        self._name = name
        self._ipAddr = ipAddr
        self._nodeID = nodeID
        self._pubKey = pubKey
        self._privateKey = privateKey

    @classmethod
    def createRandomHost(cls):
        name, dottedQ, nodeID, pubKey, privateKey = hostInfoValues()
        return cls(name, dottedQ, nodeID, pubKey, privateKey)


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
    count = 2 + rng.nextInt16(4)    # so 2 to 5 hosts
    ring = []
    for n in range(count):
        host = HostInfo.createRandomHost()
        ring.append(host)
    # DEBUG
    print("RING_DATA_VALUES returning a list of %u hosts" % len(ring))
    # END
    return ring


def hostInfoValues():
    maxCount = 8
    n = 0
    while n < maxCount:
        n = n + 1
        node = Node()  # by default uses SHA3 and generates RSA keys
        privateKey = node.key.exportKey()
        pubKey = node.pubKey.exportKey()
        hexNodeID = binascii.b2a_hex(node.nodeID)

#       # DEBUG
#       print "PRIVATE KEY: " + str(privateKey)
#       print "PUBLIC KEY:  " + repr(pubKey)
#       # END

        name = rng.nextFileName(8)

        addr = rng.nextInt32()
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
        if name in hostByName:
            continue
        if dottedQ in hostByAddr:
            continue
        if hexNodeID in hostByNodeID:       # hex value
            continue
        # DEBUG
        # print "PUB_KEY: %s" % pubKey.n
        # END
        if pubKey in hostByPubKey:
            print("pubKey is not unique")
            continue
        if privateKey in hostByPrivateKey:
            print("privateKey is not unique")
            continue

        # we require that all of these fields be unique in the sample set
        hostByName[name] = name      # dumb, but life is short
        hostByAddr[dottedQ] = name
        hostByNodeID[hexNodeID] = name
        hostByPubKey[pubKey] = name
        hostByPrivateKey[privateKey] = name

        # NOTE that nodeID is a binary value here
        return (name, dottedQ, node.nodeID, pubKey, privateKey)  # GEEP


class TestRingDataProto (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################

    def dumpBuffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    def makeSOM(self):
        # MODEL: testProtoSpec XXX
        data = StringIO(RING_DATA_PROTO_SPEC)
        p = StringProtoSpecParser(data)
        sOM = p.parse()             # object model from string serialization
        return sOM

    # actual unit tests #############################################
    def testRingDataProto(self):
        sOM = self.makeSOM()
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.ProtoSpec))
        self.assertEqual('org.xlattice.pzog.ringData', sOM.name)
        self.assertEqual(0, len(sOM.enums))
        self.assertEqual(1, len(sOM.msgs))
        self.assertEqual(0, len(sOM.seqs))

        # OUTER MESSAGE SPEC ----------------------------------------
        msgSpec = sOM.msgs[0]
        field = msgSpec[0]
        self.assertEqual(field.name, 'hosts')
        self.assertEqual(field.fTypeName, 'hostInfo')
        self.assertEqual(field.quantifier, M.Q_PLUS)

        # INNER MESSAGE SPEC ----------------------------------------
        msgSpec = sOM.msgs[0].msgs[0]
        self.assertEqual(msgSpec.fName(0), 'hostName')
        self.assertEqual(msgSpec.fTypeName(0), 'lString')
        self.assertEqual(msgSpec.fName(1), 'ipAddr')
        self.assertEqual(msgSpec.fTypeName(1), 'lString')
        self.assertEqual(msgSpec.fName(2), 'nodeID')
        self.assertEqual(msgSpec.fTypeName(2), 'fBytes32')
        self.assertEqual(msgSpec.fName(3), 'pubKey')
        self.assertEqual(msgSpec.fTypeName(3), 'lString')
        self.assertEqual(msgSpec.fName(4), 'privateKey')
        self.assertEqual(msgSpec.fTypeName(4), 'lString')
        try:
            msgSpec.fName(5)
            self.fail('did not catch reference to non-existent field')
        except IndexError as ie:
            pass                                                    # GEEP

    # ---------------------------------------------------------------
    def testCaching(self):
        """ verify that classes with the same definition are cached """
        sOM = self.makeSOM()
        protoName = sOM.name
        self.assertTrue(isinstance(sOM, M.ProtoSpec))

        outerMsgSpec = sOM.msgs[0]
        innerMsgSpec = sOM.msgs[0].msgs[0]
        OuterMsg = makeMsgClass(sOM, outerMsgSpec.name)
        # NOTE change in parent
        InnerMsg = makeMsgClass(outerMsgSpec, innerMsgSpec.name)

        # TEST INNER MESSAGE ########################################
        Clz0 = makeMsgClass(outerMsgSpec, innerMsgSpec.name)
        Clz1 = makeMsgClass(outerMsgSpec, innerMsgSpec.name)
        # we cache classes, so the two should be the same
        self.assertEqual(id(Clz0), id(Clz1))

        # test that msg instances created from the same value lists differ
        values = hostInfoValues()
        innerMsg0 = Clz0(values)
        innerMsg1 = Clz0(values)
        # we don't cache instances, so these will differ
        self.assertNotEquals(id(innerMsg0), id(innerMsg1))

        # verify that field classes are cached
        fieldSpec = innerMsgSpec[0]
        dottedName = '%s.%s' % (protoName, innerMsgSpec.name)
        F0 = makeFieldClass(dottedName, fieldSpec)
        F1 = makeFieldClass(dottedName, fieldSpec)
        self.assertEqual(id(F0), id(F1))           # GEEP

        # TEST OUTER MESSAGE ########################################
        Clz2 = makeMsgClass(sOM, outerMsgSpec.name)
        Clz3 = makeMsgClass(sOM, outerMsgSpec.name)
        # we cache classe, so the two should be the same
        self.assertEqual(id(Clz2), id(Clz3))

        # test that msg instances created from the same value lists differ
        ring = ringDataValues()  # a list of random hosts

        # 'values' is a list of field values.  In this case, the single
        # value is itself a list, a list of HostInfo value lists.
        values = [ring]            # a list whose only member is a list

        outerMsg0 = Clz2(values)
        outerMsg1 = Clz2(values)
        # we don't cache instances, so these will differ
        self.assertNotEquals(id(outerMsg0), id(outerMsg1))

        fieldSpec = outerMsgSpec[0]
        dottedName = '%s.%s' % (protoName, outerMsgSpec.name)
        F0 = makeFieldClass(dottedName, fieldSpec)
        F1 = makeFieldClass(dottedName, fieldSpec)
        self.assertEqual(id(F0), id(F1))           # GEEP

    # ---------------------------------------------------------------
    def testRingDataProtoSerialization(self):
        sOM = self.makeSOM()
        protoName = sOM.name
        outerMsgSpec = sOM.msgs[0]
        innerMsgSpec = sOM.msgs[0].msgs[0]
        OuterMsg = makeMsgClass(sOM, outerMsgSpec.name)
        # NOTE change in parent
        InnerMsg = makeMsgClass(outerMsgSpec, innerMsgSpec.name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create a message instance ---------------------------------

        # create some HostInfo instances
        count = 2 + rng.nextInt16(7)  # so 2 .. 8
        ring = []
        for n in range(count):
            # should avoid dupes
            values = hostInfoValues()
            ring.append(InnerMsg(values))

        outerMsg = OuterMsg([ring])     # a list whose member is a list

        # serialize the object to the channel -----------------------
        n = outerMsg.writeStandAlone(chan)

        oldPosition = chan.position
        chan.flip()
        self.assertEqual(oldPosition, chan.limit)
        self.assertEqual(0, chan.position)

        # deserialize the channel, making a clone of the message ----
        (readBack, n2) = OuterMsg.read(chan, sOM)
        self.assertIsNotNone(readBack)

        # verify that the messages are identical --------------------
        self.assertTrue(outerMsg.__eq__(readBack))
        self.assertEqual(n, n2)

        # produce another message from the same values --------------
        outerMsg2 = OuterMsg([ring])
        chan2 = Channel(BUFSIZE)
        n = outerMsg2.writeStandAlone(chan2)
        chan2.flip()
        (copy2, n3) = OuterMsg.read(chan2, sOM)
        self.assertTrue(outerMsg.__eq__(copy2))
        self.assertTrue(outerMsg2.__eq__(copy2))                   # GEEP

    # ---------------------------------------------------------------
    def roundTripRingDataInstanceToWireFormat(self, spec, r):  # r = ringHost

        # invoke WireMsgSpecWriter
        # XXX STUB

        # invoke WireMsgSpecParser
        # XXX STUB

        pass

    def testRoundTripRingDataInstancesToWireFormat(self):
        strSpec = StringIO(RING_DATA_PROTO_SPEC)
        p = StringProtoSpecParser(strSpec)
        ringDataSpec = p.parse()

        count = 3 + rng.nextInt16(6)   # so 3..8 inclusive

        # make that many semi-random nodes, taking care to avoid duplicates,
        # and round-trip each
        for k in range(count):
            r = HostInfo.createRandomHost()
            self.roundTripRingDataInstanceToWireFormat(ringDataSpec, r)  # GEEP


if __name__ == '__main__':
    unittest.main()
