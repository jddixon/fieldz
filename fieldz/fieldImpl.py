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

    @classmethod
    def __prepare__(meta, name, bases, **kwargs):
        """
        Allows us to pass arguments which become class attributes.
        """
        return dict(kwargs)

    def __new__(meta, name, bases, namespace, **kwargs):
        # DEBUG
        # removed namespace from print
        print("\nMetaField NEW, meta='%s',\n\tname='%s', bases='%s'" % (
            meta, name, bases))
        sys.stdout.flush()
        # END
        return super().__new__(meta, name, bases, namespace)

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
    print('MAKE_FIELD_CLASS for %s' % qualName)
    # END
    if qualName in fieldClsByQName:
        return fieldClsByQName[qualName]

    # We want an attribute and a property for each fieldSpec attr.
    # This needs to be elaborated as appropriate to deal with the
    # 18 or so field types.

    __fieldNbr = property(myFieldNbr)
    __quantifier = property(myQuantifier)
    __value = property(myValueGetter, myValueSetter)

#   class M(metaclass=MetaField,
#       _name=fieldSpec.name,
#       # PROBLEM: THIS IS A SECOND USE OF THE ATTRIBUTE 'name'
#       # name=property(myName),
#       dummy2=0,
#       _fType=fieldSpec.fTypeNdx,
#       fType=property(myFType),
#       _quantifier=fieldSpec.quantifier,
#       quantifier=__quantifier,
#       _fieldNbr=fieldSpec.fieldNbr,
#       fieldNbr=__fieldNbr,
#       _default=fieldSpec.default,
#       default=property(myDefault),
#       value=__value,
#       dummy=0):
#       pass

    class M(metaclass=MetaField,
            _name=fieldSpec.name,
            # PROBLEM: THIS IS A SECOND USE OF THE ATTRIBUTE 'name'
            # name=property(myName),
            fType=myFType,
            quantifier=fieldSpec.quantifier,
            quantifier=__quantifier,
            fieldNbr=fieldSpec.fieldNbr,
            default=fieldSpec.default):
        pass
    #----------------------------
    # possibly some more fiddling ...
    #----------------------------

    fieldClsByQName[qualName] = M
    return M
