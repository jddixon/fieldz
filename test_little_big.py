#!/usr/bin/env python3

# testLittleBig.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

# XXX FAILS to import write if named 'putter':
from fieldz.msg_impl import make_msg_class,\
    make_field_class

from fieldz.parser import StringProtoSpecParser
import fieldz.field_types as F
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel

#################################################################
# THIS WAS HACKED FROM testProtoSpec.py; CAN HACK MORE FROM THERE
#################################################################

# PROTOCOLS ---------------------------------------------------------
from little_big_test import LITTLE_BIG_PROTO_SPEC

BUFSIZE = 16 * 1024

# TESTS -------------------------------------------------------------


class TestLittleBig(unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())
        data = StringIO(LITTLE_BIG_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        self.str_obj_model = ppp.parse()     # object model from string serialization
        self.proto_name = self.str_obj_model.name  # the dotted name of the protocol

    def tearDown(self):
        pass

    # utility functions #############################################

    def lil_big_msg_values(self):
        values = []
        # XXX these MUST be kept in sync with littleBigTest.py
        values.append(self.rng.next_boolean())       # vBoolReqField
        values.append(self.rng.next_int16())         # vEnumReqField

        values.append(self.rng.next_int32())         # vuInt32ReqField
        values.append(self.rng.next_int32())         # vuInt64ReqField
        values.append(self.rng.next_int64())         # vsInt32ReqField
        values.append(self.rng.next_int64())         # vsInt64ReqField

        # #vuInt32ReqField
        # #vuInt64ReqField

        values.append(self.rng.next_int32())         # fsInt32ReqField
        values.append(self.rng.next_int32())         # fuInt32ReqField
        values.append(self.rng.next_real())          # fFloatReqField

        values.append(self.rng.next_int64())         # fsInt64ReqField
        values.append(self.rng.next_int64())         # fuInt64ReqField
        values.append(self.rng.next_real())          # fDoubleReqField

        values.append(self.rng.next_file_name(16))    # lStringReqField

        rnd_len = 16 + self.rng.next_int16(49)
        byte_buf = bytearray(rnd_len)
        self.rng.next_bytes(byte_buf)
        values.append(bytes(byte_buf))               # lBytesReqField

        b128_buf = bytearray(16)
        self.rng.next_bytes(b128_buf)
        values.append(bytes(b128_buf))               # fBytes16ReqField

        b160_buf = bytearray(20)
        self.rng.next_bytes(b160_buf)
        values.append(bytes(b160_buf))               # fBytes20ReqField

        b256_buf = bytearray(32)
        self.rng.next_bytes(b256_buf)
        values.append(bytes(b256_buf))               # fBytes32ReqField

        return values

    # actual unit tests #############################################
    def check_field_impl_against_spec(
            self, proto_name, msg_name, field_spec, value):
        self.assertIsNotNone(field_spec)
        dotted_name = "%s.%s" % (proto_name, msg_name)
        Cls = make_field_class(dotted_name, field_spec)
        if '__dict__' in dir(Cls):
            print('\nGENERATED FieldImpl CLASS DICTIONARY')
            for exc in list(Cls.__dict__.keys()):
                print("%-20s %s" % (exc, Cls.__dict__[exc]))

        self.assertIsNotNone(Cls)
        file = Cls(value)
        self.assertIsNotNone(file)

        # class attributes --------------------------------
        self.assertEqual(field_spec.name, file.name)
        self.assertEqual(field_spec.FIELD_TYPE_NDX, file.field_type)
        self.assertEqual(field_spec.quantifier, file.quantifier)
        self.assertEqual(field_spec.field_nbr, file.field_nbr)
        self.assertIsNone(file.default)          # not an elegant test

        # instance attribute ------------------------------
        self.assertEqual(value, file.value)

        # with slots enabled, this is never seen ----------
        # because __dict__ is not in the list of valid
        # attributes for f
        if '__dict__' in dir(file):
            print('\nGENERATED FieldImpl INSTANCE DICTIONARY')
            for item in list(file.__dict__.keys()):
                print("%-20s %s" % (item, file.__dict__[item]))     # GEEP

    def test_field_impl(self):
        msg_spec = self.str_obj_model.msgs[0]

        # the fields in this imaginary logEntry
        values = self.lil_big_msg_values()

        for i in range(len(msg_spec)):
            print(
                "\nDEBUG: field %u ------------------------------------------------------" %
                i)
            field_spec = msg_spec[i]
            self.check_field_impl_against_spec(
                self.proto_name, msg_spec.name, field_spec, values[i])

    def test_caching(self):
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        # XXX A HACK WHILE WE CHANGE INTERFACE ------------
        msg_spec = self.str_obj_model.msgs[0]
        name = msg_spec.name

        Clz0 = make_msg_class(self.str_obj_model, name)
        # DEBUG
        print("Constructed Clz0 name is '%s'" % Clz0.name)
        # END
        self.assertEqual(name, Clz0.name)
        Clz1 = make_msg_class(self.str_obj_model, name)
        self.assertEqual(name, Clz1.name)

        # END HACK ----------------------------------------
        # we cache classe, so the two should be the same
        self.assertEqual(id(Clz0), id(Clz1))

        # chan    = Channel(BUFSIZE)
        values = self.lil_big_msg_values()
        lil_big_msg0 = Clz0(values)
        lil_big_msg1 = Clz0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(lil_big_msg0), id(lil_big_msg1))

        field_spec = msg_spec[0]
        dotted_name = "%s.%s" % (self.proto_name, msg_spec.name)
        F0 = make_field_class(dotted_name, field_spec)
        F1 = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(F0), id(F1))

    def testLittleBig(self):
        self.assertIsNotNone(self.str_obj_model)
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.fieldz.test.littleBigProto',
                         self.str_obj_model.name)

        self.assertEqual(0, len(self.str_obj_model.enums))
        self.assertEqual(1, len(self.str_obj_model.msgs))
        self.assertEqual(0, len(self.str_obj_model.seqs))

        msg_spec = self.str_obj_model.msgs[0]

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LittleBigMsg class ------------------------------
        LittleBigMsg = make_msg_class(self.str_obj_model, msg_spec.name)

        # -------------------------------------------------------------
        # XXX the following fails because field 2 is seen as a property
        # instead of a list
        if False:        # DEBUGGING
            print('\nLittleBigMsg CLASS DICTIONARY')
            for (ndx, key) in enumerate(LittleBigMsg.__dict__.keys()):
                print("%3u: %-20s %s" % (ndx, key, LittleBigMsg.__dict__[key]))
        # -------------------------------------------------------------

        # create a message instance ---------------------------------
        values = self.lil_big_msg_values()            # quasi-random values
        lil_big_msg = LittleBigMsg(values)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes.  This works at the class level but
        # NOT at the instance level
        #
        if True:
            try:
                lil_big_msg.foo = 42
                self.fail(
                    "ERROR: attempt to assign new instance attribute succeeded")
            except AttributeError as a_exc:
                # DEBUG
                print(
                    "ATTR ERROR ATTEMPTING TO SET lilBigMsg.foo: " +
                    str(a_exc))
                # END
                pass

        if '__dict__' in dir(lil_big_msg):
            print('\nlilBigMsg INSTANCE DICTIONARY')
            for exc in list(lil_big_msg.__dict__.keys()):
                print("%-20s %s" % (exc, lil_big_msg.__dict__[exc]))

        # lilBigMsg.name is a property
        try:
            lil_big_msg.name = 'boo'
            self.fail("ERROR: attempt to change message name succeeded")
        except AttributeError:
            pass

        self.assertEqual(msg_spec.name, lil_big_msg.name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(lil_big_msg.enums))
        self.assertEqual(0, len(lil_big_msg.msgs))

        self.assertEqual(17, len(lil_big_msg.field_classes))
        # number of fields in instance
        self.assertEqual(17, len(lil_big_msg))
        for i in range(len(lil_big_msg)):
            self.assertEqual(values[i], lil_big_msg[i].value)

        # serialize the object to the channel -----------------------
        print("\nDEBUG: PHASE A ######################################")
        nnn = lil_big_msg.write_stand_alone(chan)

        old_position = chan.position
        chan.flip()
        self.assertEqual(old_position, chan.limit)
        self.assertEqual(0, chan.position)

        # deserialize the channel, making a clone of the message ----
        (read_back, nn2) = LittleBigMsg.read(
            chan, self.str_obj_model)  # sOM is protoSpec
        self.assertIsNotNone(read_back)
        self.assertEqual(nnn, nn2)

        # verify that the messages are identical --------------------
        self.assertTrue(lil_big_msg.__eq__(read_back))

        print("\nDEBUG: PHASE B ######################################")
        # produce another message from the same values --------------
        lil_big_msg2 = LittleBigMsg(values)
        chan2 = Channel(BUFSIZE)
        nnn = lil_big_msg2.write_stand_alone(chan2)
        chan2.flip()
        (copy2, nn3) = LittleBigMsg.read(chan2, self.str_obj_model)
        self.assertIsNotNone(copy2)
        self.assertEqual(nnn, nn3)
        self.assertTrue(lil_big_msg.__eq__(copy2))
        self.assertTrue(lil_big_msg2.__eq__(copy2))

        # test clear()
        chan2.position = 97
        chan2.limit = 107
        chan2.clear()
        self.assertEqual(0, chan2.limit)
        self.assertEqual(0, chan2.position)

if __name__ == '__main__':
    unittest.main()
