#!/usr/bin/env python3

# testGenEnum.py

import time
import unittest


class EnumError(RuntimeError):
    pass


def saferSetter(obj, sym, value):
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

    def __init__(self, a, b):
        print("GeneratedEnum object: a = %s, b = %s" % (a, b))

    def foo(self, whatever):
        print("foo called with param %s" % str(whatever))

    barAttr = 47


class TestGenEnum (unittest.TestCase):

    def setUp(self): pass

    def tearDown(self): pass

    # utility functions #############################################

    # actual unit tests #############################################
    def testGenEnum(self):
        g = GeneratedEnum(13, 97)
        print("ABOUT TO CREATE SECOND INSTANCE")
        h = GeneratedEnum(13, 97)

    def testGeneratingClass(self):
        class F(metaclass=MetaEnum,
                A=3, B=7, C=11, echo=echo, __setattr__=saferSetter):
            pass
        f = F()

        # the keywords passed result in instance attributes
        self.assertEqual(3, f.A)
        self.assertEqual(7, f.B)
        self.assertEqual(11, f.C)

        # ... not class attributes
        try:
            F.A
        except AttributeError:
            pass

        # 'bound method' != function
        # self.assertEqual(f.echo, echo)

        # 'bound method' != function
        # self.assertEqual(F.__setattr__, saferSetter)

        f = F()
        f.echo('I printed this using F.echo()')

        self.assertEqual(f.C, 11)
        try:
            f.C = 137
            self.assertEqual(137, f.C)
            self.fail('ERROR: successfully changed value of f.C')
        except EnumError:
            # success: caught attempt to set new symbol
            pass

if __name__ == '__main__':
    unittest.main()
