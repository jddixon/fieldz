#!/usr/bin/env python3

# test_msgImpl.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
# import fieldz.field_types as F
import fieldz.msg_spec as M
# import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class, MsgImpl


#################################################################
# THIS WAS HACKED FROM testProtoSpec.py; CAN HACK MORE FROM THERE
#################################################################

# PROTOCOLS ---------------------------------------------------------
from little_big_test import LITTLE_BIG_PROTO_SPEC

from fieldz.simple_protocol import SIMPLE_PROTOCOL
from fieldz.zoggery_proto_spec import ZOGGERY_PROTO_SPEC
from fieldz.nested_enum_proto_spec import NESTED_ENUM_PROTO_SPEC
from fieldz.nested_msgs_proto_spec import NESTED_MSGS_PROTO_SPEC

BUFSIZE = 16 * 1024
RNG = SimpleRNG(time.time())

# TESTS -------------------------------------------------------------


class TestMsgImpl(unittest.TestCase):

    def setUp(self):
        data = StringIO(ZOGGERY_PROTO_SPEC)
        ppp = StringProtoSpecParser(data)   # data should be file-like
        self.assertTrue(ppp is not None)
        self.str_obj_model = ppp.parse()     # object model from string serialization
        self.assertTrue(self.str_obj_model is not None)
        self.proto_name = self.str_obj_model.name  # the dotted name of the protocol
        # DEBUG
        print("setUp: proto name is %s" % self.proto_name)
        # END

    def tearDown(self):
        pass

    # utility functions #############################################
    def le_msg_values(self):
        """ returns a list """
        timestamp = int(time.time())
        node_id = [0] * 20
        key = [0] * 20
        length = RNG.next_int32(256 * 256)
        # let's have some random bytes
        RNG.next_bytes(node_id)
        RNG.next_bytes(key)
        by_ = 'who is responsible'
        path = '/home/jdd/tarballs/something.tar.gz'
        return [timestamp, node_id, key, length, by_, path]

    # NOT YET USED HERE
    def little_big_values(self):
        values = []
        # XXX these MUST be kept in sync with littleBigTest.py
        values.append(RNG.next_boolean())       # vBoolReqField
        values.append(RNG.next_int16())         # vEnumReqField

        values.append(RNG.next_int32())         # vuInt32ReqField
        values.append(RNG.next_int32())         # vuInt64ReqField
        values.append(RNG.next_int64())         # vsInt32ReqField
        values.append(RNG.next_int64())         # vsInt64ReqField

        # #vuInt32ReqField
        # #vuInt64ReqField

        values.append(RNG.next_int32())         # fsInt32ReqField
        values.append(RNG.next_int32())         # fuInt32ReqField
        values.append(RNG.next_real())          # fFloatReqField

        values.append(RNG.next_int64())         # fsInt64ReqField
        values.append(RNG.next_int64())         # fuInt64ReqField
        values.append(RNG.next_real())          # fDoubleReqField

        values.append(RNG.next_file_name(16))    # lStringReqField

        rnd_len = 16 + RNG.next_int16(49)
        byte_buf = bytearray(rnd_len)
        values.append(RNG.next_bytes(byte_buf))  # lBytesReqField

        b128_buf = bytearray(16)
        values.append(RNG.next_bytes(b128_buf))  # fBytes16ReqField

        b160_buf = bytearray(20)
        values.append(RNG.next_bytes(b160_buf))  # fBytes20ReqField

        b256_buf = bytearray(32)
        values.append(RNG.next_bytes(b256_buf))  # fBytes32ReqField  GEEP

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
        file = cls(value)
        self.assertIsNotNone(file)

        # instance attributes -----------------------------
        self.assertEqual(field_spec.name, file.name)
        self.assertEqual(field_spec.field_type_ndx, file.field_type)
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
        values = self.le_msg_values()

        for i in range(len(msg_spec)):
            print(
                "\nDEBUG: field %u ------------------------------------------------------" %
                i)
            field_spec = msg_spec[i]
            self.check_field_impl_against_spec(
                self.proto_name, msg_spec.name, field_spec, values[i])

    def test_caching(self):
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        msg_spec = self.str_obj_model.msgs[0]
        name = msg_spec.name
        cls0 = make_msg_class(self.str_obj_model, name)
        cls1 = make_msg_class(self.str_obj_model, name)
        # we cache classe, so the two should be the same
        self.assertEqual(id(cls0), id(cls1))

        # chan    = Channel(BUFSIZE)
        values = self.le_msg_values()
        le_msg0 = cls0(values)
        le_msg1 = cls0(values)
        # we don't cache instances, so these will differ
        self.assertNotEqual(id(le_msg0), id(le_msg1))

        field_spec = msg_spec[0]
        dotted_name = "%s.%s" % (self.proto_name, msg_spec.name)
        f0cls = make_field_class(dotted_name, field_spec)
        f1cls = make_field_class(dotted_name, field_spec)
        self.assertEqual(id(f0cls), id(f1cls))           # GEEP

    def test_msg_impl(self):
        self.assertIsNotNone(self.str_obj_model)
        self.assertTrue(isinstance(self.str_obj_model, M.ProtoSpec))
        self.assertEqual('org.xlattice.zoggery', self.str_obj_model.name)

        self.assertEqual(0, len(self.str_obj_model.enums))
        self.assertEqual(1, len(self.str_obj_model.msgs))
        self.assertEqual(0, len(self.str_obj_model.seqs))

        msg_spec = self.str_obj_model.msgs[0]

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the LogEntryMsg class ------------------------------

        log_entry_msg_cls = make_msg_class(self.str_obj_model, msg_spec.name)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes

        # TEST TEMPORARILY DISABLED
#        try:
#            LogEntryMsg.foo = 42
#            self.fail(
#                "ERROR: attempt to assign new class attribute succeeded")
#        except AttributeError as ae:
#
#            # DEBUG
#            print(
#                "success: attr error attempting to set LogEntryMsg.foo: " +
#                str(ae))
#            # END
#            pass                # GEEP

        # create a message instance ---------------------------------
        values = self.le_msg_values()            # quasi-random values
        le_msg = log_entry_msg_cls(values)

        # __setattr__ in MetaMsg raises exception on any attempt
        # to add new attributes.  This works at the class level but
        # NOT at the instance level
        if False:
            try:
                le_msg.foo = 42
                self.fail(
                    "ERROR: attempt to assign new instance attribute succeeded")
            except AttributeError as a_exc:
                # DEBUG
                print("ATTR ERROR ATTEMPTING TO SET leMsg.foo: " + str(a_exc))
                # END
                # pass

        # leMsg._name is a property
        # TEST TEMPORARILY DISABLED
#        try:
#            leMsg._name = 'boo'
#            self.fail("ERROR: attempt to change message name succeeded")
#        except AttributeError:
#            pass

        self.assertEqual(msg_spec.name, le_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(le_msg.enums))
        self.assertEqual(0, len(le_msg.msgs))

        self.assertEqual(6, len(le_msg.field_classes))
        self.assertEqual(6, len(le_msg))        # number of fields in instance
        # TEST TEMPORARILY DISABLED
#        for i in range(len(leMsg)):
#            self.assertEqual(values[i], leMsg[i].value)

        ################################
        # XXX FIELDS ARE NOT AS EXPECTED
        ################################

        # verify fields are accessible in the object ----------------
        # DEBUG
        for field in le_msg._fieldClasses:
            print("FIELD: %s = %s " % (field.name, field.value))
        # END
        (timestamp, node_id, key, length, by_, path) = tuple(values)
        # FAILS: null timestamp
        self.assertEqual(timestamp, le_msg.timestamp)

        self.assertEqual(node_id, le_msg.node_id)
        self.assertEqual(key, le_msg.key)
        self.assertEqual(length, le_msg.length)
        self.assertEqual(by_, le_msg.by_)
        self.assertEqual(path, le_msg.path)

        # serialize the object to the channel -----------------------
        # XXX not a public method
        expected_msg_len = le_msg._wire_len()
        print("EXPECTED LENGTH OF SERIALIZED OBJECT: %u" % expected_msg_len)
        buf = chan.buffer

        chan.clear()

        nnn = le_msg.write_stand_alone(chan)                 # n is class index
        old_position = chan.position                     # TESTING flip()
        chan.flip()
        self.assertEqual(old_position, chan.limit)      # TESTING flip()
        self.assertEqual(0, chan.position)   # TESTING flip()
        actual = chan.limit

        # deserialize the channel, making a clone of the message ----
        # XXX FAILS BECAUSE HEADER IS PRESENT:
        #(readBack,n2) = LogEntryMsg.read(chan, self.sOM)
        (read_back, nn2) = MsgImpl.read(chan, self.str_obj_model)
        self.assertIsNotNone(read_back)
        self.assertTrue(le_msg.__eq__(read_back))
        self.assertEqual(nnn, nn2)

        # produce another message from the same values --------------
        le_msg2 = log_entry_msg_cls(values)
        chan2 = Channel(BUFSIZE)
        nnn = le_msg2.write_stand_alone(chan2)
        chan2.flip()
        (copy2, nn3) = log_entry_msg_cls.read(chan2, self.str_obj_model)
        self.assertTrue(le_msg.__eq__(copy2))
        self.assertTrue(le_msg2.__eq__(copy2))

#   def test_msg(self):
#       # Testing MsgSpec with simple fields.  Verify that read,
#       # putter, lenFunc, and pLenFunc work for the basic types
#       # (ie, that they are correctly imported into this reg) and
#       # they are work for the newly defined single-msg protoSpec.

#       # Use ZOGGERY_PROTO_SPEC

#       # parse the protoSpec
#       # verify that this adds 1 (msg) + 5 (field count) to the number
#       # of entries in getters, putters, etc

#       pass

#   def test_enum(self):
#       # need to verify that getter, putter, lenFunc, and pLenFunc work
#       # for enums and nested enums

#       # Use NESTED_ENUM_PROTO_SPEC
#       # XXX STUB XXX

#       pass

#   def test_nested_msgs(self):
#       # Test MsgSpec with embedded msg and enum fields, to a depth of
#       # at least 3.  Need to verify that getter, putter, lenFunc, and
#       # pLenFunc work.

#       # Use NESTED_MSGS_PROTO_SPEC
#       # XXX STUB XXX

#       pass    # GEEP

if __name__ == '__main__':
    unittest.main()
