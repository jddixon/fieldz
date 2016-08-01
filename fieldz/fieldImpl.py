# ~/dev/py/fieldz/fieldz/fieldImpl.py

import sys   # for debugging

from fieldz.msgSpec import FieldSpec

# XXX THIS IS UNSAFE!!! XXX
fieldClsByQName = {}        # PROTO_NAME . MSG_NAME . FIELD_NAME => class

# -------------------------------------------------------------------
# CODE FRAGMENTS
# -------------------------------------------------------------------


def myName(self): return self._name


def myFType(cls): return cls._fType


def myQuantifier(cls): return cls._quantifier


def myFieldNbr(cls): return cls._fieldNbr


def myDefault(cls): return cls._default

# these get and set the value attribute of the field instance; they
# have nothing to do with de/serialization to and from the channel


def myValueGetter(self): return self._value


def myValueSetter(self, value): self._value = value

# -------------------------------------------------------------------
# FIELD CLASS
# -------------------------------------------------------------------


class FieldImpl(object):
    """
    An abstract class intended to serve as parent to automatically
    generated classes whose purpose will be to ease user handling
    of data being sent or received across the wire.
    """

    #################################################################
    # NOTE: if we inherit from type, we get a TypeError: nonempty
    # __slots__ not supported for subtype of type
    #################################################################
    __slots__ = ['_value', ]

    # should default precede value?  if a value is assigned, isn't that
    # a default?  In fact shouldn't the parameter list end with
    #   value=default?
    def __init__(self, value=None):
        # XXX NEED SOME VALIDATION
        self._value = value

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        if self._name != other._name:
            return False
        if self._fType != other._fType:
            return False
        if self._quantifier != other._quantifier:
            return False
        if self._fieldNbr != other._fieldNbr:
            return False
        # ignore defaults for now
        return True


class MetaField(type):

    def __new__(cls, name, bases, namespace, **kwargs):
        # DEBUG
        # removed namespace from print
        print("\nMetaField NEW, cls='%s',\n\tname='%s', bases='%s'" % (
            cls, name, bases))
        sys.stdout.flush()
        # END
        return super().__new__(cls, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)

        # DEBUG without namespace
        print("MetaField INIT, cls='%s',\n\tname='%s', bases='%s'" % (
            cls, name, bases))
        sys.stdout.flush()
        # END

# -- MAKER ----------------------------------------------------------


def makeFieldClass(dottedMsgName, fieldSpec):
    if dottedMsgName is None:
        raise ValueError('null message name')
    if fieldSpec is None:
        raise ValueError('null field spec')
    qualName = '%s.%s' % (dottedMsgName, fieldSpec.name)
    # DEBUG
    # print('MAKE_FIELD_CLASS for %s' % qualName)
    # END
    if qualName in fieldClsByQName:
        return fieldClsByQName[qualName]

#   # DEBUG
#   # won't work if FieldSpec has __slots__
#   if '__dict__' in dir(FieldSpec):
#       print("FieldSpec CLASS DICTIONARY excluding __doc__")
#       for key in list(FieldSpec.__dict__.keys()):
#           if key != '__doc__':
#               print("    %-20s %s" % (key, FieldSpec.__dict__[key]))
#       print("fieldSpec INSTANCE DICTIONARY excluding __doc__")

#   if '__dict__' in dir(fieldSpec):
#       for key in list(fieldSpec.__dict__.keys()):
#           if key != '__doc__':
#               print("    %-20s %s" % (key, fieldSpec.__dict__[key]))
#   # END

    d = {}

    # disable __slots__ until better understood
    # d['__slots__'] = ['_name', '_fType', '_quantifier',
    #                  '_fieldNbr', '_default', ]

    # we want an attribute and a property for each fieldSpec attr
    d['_name'] = fieldSpec.name
    d['name'] = property(myName)
    d['_fType'] = fieldSpec.fTypeNdx
    d['fType'] = property(myFType)
    d['_quantifier'] = fieldSpec.quantifier
    d['quantifier'] = property(myQuantifier)
    d['_fieldNbr'] = fieldSpec.fieldNbr
    d['fieldNbr'] = property(myFieldNbr)
    d['_default'] = fieldSpec.default
    d['default'] = property(myDefault)

    # this needs to be elaborated as appropriate to deal with the
    # 18 or so field types
    d['value'] = property(myValueGetter, myValueSetter)

    M = MetaField(str(fieldSpec.name),      # name
                  (FieldImpl,),             # bases
                  d)                        # dictionary

    #----------------------------
    # possibly some more fiddling ...
    #----------------------------

    fieldClsByQName[qualName] = M
    return M
