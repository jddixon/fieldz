#!/usr/bin/env python3

# testGenEnum.py

import time
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
    def __prepare__(meta, name, bases, **kwargs):
        """
        Required: we are passing arguments which become class attributes.
        """
        return dict(kwargs)

    def __new__(meta, name, bases, namespace, **kwargs):
        print("METACLASS NEW gets called once")
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, name, bases, namespace, **kwargs):
        super(MetaEnum, cls).__init__(name, bases, namespace)


class GeneratedEnum(metaclass=MetaEnum):

    def __init__(self, aVal, b_val):
        print("GeneratedEnum object: a = %s, b = %s" % (aVal, b_val))

    def foo(self, whatever):
        print("foo called with param %s" % str(whatever))

    barAttr = 47


class TestGenEnum (unittest.TestCase):

    def setUp(self): pass

    def tearDown(self): pass

    # utility functions #############################################

    # actual unit tests #############################################
    def test_gen_enum(self):
        enum1 = GeneratedEnum(13, 97)
        print("ABOUT TO CREATE SECOND INSTANCE")
        enum2 = GeneratedEnum(13, 97)

    def testGeneratingClass(self):
        class F(metaclass=MetaEnum,
                A=3, B=7, C=11, echo=echo, __setattr__=safer_setter):
            pass
        file = F()

        # the keywords passed result in instance attributes
        self.assertEqual(3, file.A)
        self.assertEqual(7, file.B)
        self.assertEqual(11, file.C)

        # ... not class attributes
        try:
            F.A
        except AttributeError:
            pass

        # 'bound method' != function
        # self.assertEqual(f.echo, echo)

        # 'bound method' != function
        # self.assertEqual(F.__setattr__, saferSetter)

        file = F()
        file.echo('I printed this using F.echo()')

        self.assertEqual(file.C, 11)
        try:
            file.C = 137
            self.assertEqual(137, file.C)
            self.fail('ERROR: successfully changed value of f.C')
        except EnumError:
            # success: caught attempt to set new symbol
            pass

if __name__ == '__main__':
    unittest.main()
