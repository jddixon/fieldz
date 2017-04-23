#!/usr/bin/env python3

# testGenEnum.py

import unittest


class EnumError(RuntimeError):
    pass


def safer_setter(obj, sym, value):
    """ object attributes may be set but never reset """

    try:
        val = obj.__getattribute__(sym)
        # we get here if sym is defined`
        raise EnumError(
            'attempt to change value of constant ' + sym)
    except AttributeError:
        obj.sym = value


def echo(cls, text):
    print(text)


class MetaEnum(type):

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        """
        Required: we are passing arguments which become class attributes.
        """
        return dict(kwargs)

    def __new__(mcs, name, bases, namespace, **kwargs):
        print("METACLASS NEW gets called once")
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super(MetaEnum, cls).__init__(name, bases, namespace)


class GeneratedEnum(metaclass=MetaEnum):

    def __init__(self, aaa, bbb):
        print("GeneratedEnum object: aaa = %s, bbb = %s" % (aaa, bbb))

    def foo_(self, whatever):
        print("foo_ called with param %s" % str(whatever))

    barAttr = 47


class TestGenEnum(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def test_gen_enum(self):
        enum1 = GeneratedEnum(13, 97)
        print("ABOUT TO CREATE SECOND INSTANCE")
        enum2 = GeneratedEnum(13, 97)

    def test_generating_class(self):
        class FCls(metaclass=MetaEnum,
                   aaa=3, bbb=7, ccc=11,
                   echo=echo, __setattr__=safer_setter):
            pass
        f_inst = FCls()

        # the keywords passed result in instance attributes
        # pylint can't cope with dynamic classes
        # pylint: disable=no-member
        self.assertEqual(3, f_inst.aaa)
        self.assertEqual(7, f_inst.bbb)
        self.assertEqual(11, f_inst.ccc)

        # ... not class attributes
        try:
            FCls.aaa
        except AttributeError:
            pass

        # 'bound method' != function
        # self.assertEqual(f.echo, echo)

        # 'bound method' != function
        # self.assertEqual(FCls.__setattr__, saferSetter)

        f_inst = FCls()
        f_inst.echo('I printed this using FCls.echo()')

        self.assertEqual(f_inst.ccc, 11)
        try:
            f_inst.ccc = 137
            self.assertEqual(137, f_inst.ccc)
            self.fail('ERROR: successfully changed value of f.ccc')
        except EnumError:
            # success: caught attempt to set new symbol
            pass


if __name__ == '__main__':
    unittest.main()
