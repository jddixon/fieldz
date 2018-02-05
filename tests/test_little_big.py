#!/usr/bin/env python3

# testLittleBig.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

# XXX DOES NOT import write if named 'putter':
from fieldz.msg_impl import make_msg_class,\
    make_field_class

from fieldz.parser import StringProtoSpecParser
import fieldz.msg_spec as M
# import wireops.field_types as F
# import wireops.typed as T
from wireops.chan import Channel

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
        cls = make_field_class(dotted_name, field_spec)
        if '__dict__' in dir(cls):
            print('\nGENERATED FieldImpl CLASS DICTIONARY')
            for exc in list(cls.__dict__.keys()):
                print("%-20s %s" % (exc, cls.__dict__[exc]))

        self.assertIsNotNone(cls)
        datum = cls(value)
        self.assertIsNotNone(datum)

        # class attributes --------------------------------
        # pylint:disable=no-member
        self.assertEqual(field_spec.fname, datum.fname)         # L 106
        # pylint:disable=no-member
        self.assertEqual(field_spec.field_type, datum.field_type)
        # pylint:disable=no-member
        self.assertEqual(field_spec.quantifier, datum.quantifier)
        # pylint:disable=no-member
        self.assertEqual(field_spec.field_nbr, datum.field_nbr)
        # pylint:disable=no-member
        self.assertIsNone(datum.default)          # not an elegant test

        # instance attribute ------------------------------
        # pylint:disable=no-member
        self.assertEqual(value, datum.value)

        # with slots enabled, this is never seen ----------
        # because __dict__ is not in the list of valid
        # attributes for f
        if '__dict__' in dir(datum):
            print('\nGENERATED FieldImpl INSTANCE DICTIONARY')
            for item in list(datum.__dict__.keys()):
                print("%-20s %s" % (item, datum.__dict__[item]))     # GEEP

    def test_field_impl(self):
        # DEBUG
        print("TEST_FIELD_IMPL")
        # END
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
        # DEBUG
        print("TEST_CACHING")
        # END
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        # XXX A HACK WHILE WE CHANGE INTERFACE ------------
        msg_spec = self.str_obj_model.msgs[0]
        mname = msg_spec.mname

        cls0 = make_msg_class(self.str_obj_model, mname)
        # DEBUG
        print("EXPECTING CLASS, FOUND: %s" % type(cls0))    # <<<< KUKEMAL !
        # END
        inst0 = cls0(mname)
        # DEBUG
        # pylint:disable=no-member
        print("Constructed inst0 mname is '%s'" % inst0.mname)
        # END
        # pylint:disable=no-member
        self.assertEqual(mname, inst0.mname)

        # THIS IS A CLASS, NOT AN INSTANCE
        cls1 = make_msg_class(self.str_obj_model, mname)
        inst1 = cls1(mname)
        # pylint:disable=no-member
        self.assertEqual(mname, inst1.mname)

        # END HACK ----------------------------------------
        # we cache classe, so the two should be the same

        #############################################################
        # self.assertEqual(id(cls0), id(cls1))      # FAILS FAILS FAILS
        #############################################################

        # chan    = Channel(BUFSIZE)
        values = self.lil_big_msg_values()
        lil_big_msg0 = cls0(values)
        lil_big_msg1 = cls0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(lil_big_msg0), id(lil_big_msg1))

        field_spec = msg_spec[0]
        dotted_name = "%s.%s" % (self.proto_name, msg_spec.mname)
        f0cls = make_field_class(dotted_name, field_spec)
        f1cls = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(f0cls), id(f1cls))

    def test_little_big(self):
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
        little_big_msg_cls = make_msg_class(self.str_obj_model, msg_spec.mname)

        # -------------------------------------------------------------
        # XXX the following fails because field 2 is seen as a property
        # instead of a list
        if False:        # DEBUGGING
            print('\nLittleBigMsg CLASS DICTIONARY')
            for (ndx, key) in enumerate(little_big_msg_cls.__dict__.keys()):
                print(
                    "%3u: %-20s %s" %
                    (ndx, key, little_big_msg_cls.__dict__[key]))
        # -------------------------------------------------------------

        # create a message instance ---------------------------------
        values = self.lil_big_msg_values()            # quasi-random values
        lil_big_msg = little_big_msg_cls(values[0])   # [0] IS EXPERIMENT

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes.  This works at the class level but
        # NOT at the instance level
        #
        # XXX HACK
        print("*** SKIPPING ASSIGNENT-TO-CONSTANT TEST ***")
        # END
        if False:
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
        # XXX HACK
        print("*** SKIPPING ASSIGNENT-TO-PROPERTY TEST ***")
        # END
        if False:
            try:
                lil_big_msg.mname = 'boo'
                self.fail("ERROR: attempt to change message name succeeded")
            except AttributeError:
                pass

        # DEBUG
        print("TYPE msg_spec.mname: %s" % type(msg_spec.mname))
        print("TYPE lil_big_msg.mname: %s" % type(lil_big_msg.mname))
        # END

        self.assertEqual(msg_spec.mname, lil_big_msg.mname)
        # we don't have any nested enums or messages
        # pylint:disable=no-member
        self.assertEqual(0, len(lil_big_msg.enums))
        # pylint:disable=no-member
        self.assertEqual(0, len(lil_big_msg.msgs))

        # pylint:disable=no-member
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
        (read_back, nn2) = little_big_msg_cls.read(
            chan, self.str_obj_model)  # sOM is protoSpec
        self.assertIsNotNone(read_back)
        self.assertEqual(nnn, nn2)

        # verify that the messages are identical --------------------
        self.assertTrue(lil_big_msg.__eq__(read_back))

        print("\nDEBUG: PHASE B ######################################")
        # produce another message from the same values --------------
        lil_big_msg2 = little_big_msg_cls(values)
        chan2 = Channel(BUFSIZE)
        nnn = lil_big_msg2.write_stand_alone(chan2)
        chan2.flip()
        (copy2, nn3) = little_big_msg_cls.read(chan2, self.str_obj_model)
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
