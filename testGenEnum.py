#!/usr/bin/python

# testGenEnum.py

import time, unittest

from rnglib import SimpleRNG

class EnumError(RuntimeError):    pass

def cantSetAttr(cls, sym, value):
    """ instance variables may be set but never reset """
    if sym not in cls.__dict__:
        cls.__dict__[sym] = value
    else:
        raise EnumError(
             'attempt to change value of constant ' + sym)

def echo(cls, text):
    print(text)

class MetaEnum(type):
    def __new__(meta, name, bases, dct):
        print("METACLASS NEW gets called once")
        return super(MetaEnum, meta).__new__(meta, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(MetaEnum, cls).__init__(name, bases, dct)

        # TypeError: Error when calling the metaclass bases
        #   'dictproxy' object does not support item assignment
        # cls.__dict__['__setattr__'] = cantSetAttr
        print("METACLASS INIT gets called once")

    def __call__(cls, *args, **kwargs):
        print("CALL")
        return type.__call__(cls, *args, **kwargs)

class GeneratedEnum(object, metaclass=MetaEnum):
    def __init__(self, a, b):
        print("GeneratedEnum object: a = %s, b = %s" % (a,b))

    def foo(self, whatever):
        print("foo called with param %s" % str(whatever))

    barAttr = 47

class TestGenEnum (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def testGenEnum(self):
        print("ABOUT TO CREATE INSTANCE")
        g = GeneratedEnum(13,97)
        print("ABOUT TO CREATE SECOND INSTANCE")
        h = GeneratedEnum(13,97)

    def testGeneratingClass(self):
        F = MetaEnum('ClzF', (object,), 
                {'A':3, 'B':7, 'C':11, 
                    'echo' : echo,
                    '__setattr__': cantSetAttr })
        self.assertEquals('ClzF', F.__name__)
        self.assertEquals(3, F.A)
        self.assertEquals(7, F.B)
        self.assertEquals(11, F.C)
#       setattr(F, 'echo', echo)
#       setattr(F, '__setattr__', cantSetAttr)

        print("CLASS DICTIONARY:")
        for s in list(F.__dict__.keys()):
            print("%-20s %s" % (s, F.__dict__[s]))

        # the echo method must be bound to a class instance
        f = F()
        f.echo('I printed this using F.echo()')

        # The next tree lines don't print anything from f.__dict__,
        # because there isn't one at the instance level
        print("INSTANCE DICTIONARY:")
        for s in list(f.__dict__.keys()):
            print("%-20s %s" % (s, f.__dict__[s]))

        # This is based on a misunderstanding: does __setattr__ 
        # behave just like echo?  And so work only at the instance level?
        try:
            setattr(F, 'C', 13)
            self.assertEquals(13, F.C)
            self.fail('ERROR: successfully changed value of C')
        except EnumError:
            print('success: caught attempt to set new symbol')

if __name__ == '__main__':
    unittest.main()
