#!/usr/bin/python3

# testSolo.py
import time
import unittest

from rnglib import SimpleRNG
import fieldz.enumSpec as Q
from fieldz.reg import NodeReg

SOLO = """
protocol org.xlattice.fieldz.test

message SoloMsg
    val vuint32     # a single unsigned value, a required field
"""


class TestSolo (unittest.TestCase):
    """
    Send the definition of the msgSpec Solo down a channel followed
    by a single instance of the msgSpec.
    """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    def dumpBuffer(self, buf):
        for i in range(16):
            print("0x%02x " % buf[i], end=' ')
        print()

    # actual unit tests #############################################
    def testSolo(self):
        # Create a registry, writeReg.  (Don't need persistence at this
        # stage.)
        writeReg = NodeReg()        # 2012-11-11 was Registry()

        # Create writer, a TFWriter, and so wb, the buffer we are going to
        # write to.

        # Deserialize SOLO as soloSpec, confirming that it is an instance
        # of MsgSpec.

        # Register the soloSpec object with writeReg.

        # Verify that this has automatically created a ProtoSpec instance
        # for org.xlattice.fieldz.test

        # Write soloSpec, the SoloMsg msgSpec, to the buffer (this is a
        # class definition).

        # Create an instance of SoloMsg, set its val field to 97,
        # and write that instance to the data buffer

        # Create a TFReader using wb, the same buffer as writer.  The buffer's
        # limit will be used to see how much we read from the buffer.
        # wb.position is reset to zero.

        # Create a separate read registry, readReg.
        readReg = NodeReg()

        # Read the first message from the TFReader, deserializing it
        # as a ProtoSpec (questionable)

        # Prove that this protoSpec is identical to the writer's protoSpec

        # Read the next message from the TFReader and deserialize it.

        # Verify that this was a msgSpec for SoloMsg

        # Add the msgSpec to the reader's registry.

        # Read the next message from the TFReader and deserialize it.

        # Verify that this is an instance of SoloMsg and that its val
        # field evaluates to 97.

        pass

if __name__ == '__main__':
    unittest.main()
