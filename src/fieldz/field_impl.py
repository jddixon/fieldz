# ~/dev/py/fieldz/fieldz/fieldImpl.py

"""
Code for building Field classes.
"""

import sys   # for debugging

from fieldz import FieldzError

# from fieldz.msg_spec import FieldSpec

# IS THIS UNSAFE???

FIELD_CLS_BY_Q_NAME = {}        # PROTO_NAME . MSG_NAME . FIELD_NAME => class

# -------------------------------------------------------------------
# CODE FRAGMENTS
# -------------------------------------------------------------------


def my_name(self):
    """
    Code chunk used in creating field classes: returns field name.
    """
    # pylint: disable=protected-access
    return self._fname


def my_quantitier(cls):
    """
    Code chunk used in creating field classes: returns quantifier.
    """
    # pylint: disable=protected-access
    return cls._quantifier


def my_field_nbr(cls):
    """
    Code chunk used in creating field classes: returns field number.
    """
    # pylint: disable=protected-access
    return cls._field_nbr


def my_default(cls):
    """
    Code chunk used in creating classes: returns default.
    """
    # pylint: disable=protected-access
    return cls._default

# these get and set the value attribute of the field instance; they
# have nothing to do with de/serialization to and from the channel


def my_value_getter(self):
    """ Value getter used in constructing field class. """

    # pylint: disable=protected-access
    # DEBUG
    print("myValueGetter returning %s" % self._value)
    # END
    return self._value


def my_value_setter(self, value):
    """ Value setter used in constructing field class. """

    # DEBUG
    print("myValueSetter: value becomes %s" % value)
    # END
    # pylint: disable=protected-access
    self._value = value

# -------------------------------------------------------------------
# FIELD CLASS
# -------------------------------------------------------------------


class FieldImpl(object):
    """
    An abstract class intended to serve as parent to automatically
    generated classes whose purpose will be to ease user handling
    of data being sent or received across the wire.
    """

    # pylint: disable=too-few-public-methods

    #################################################################
    # NOTE: if we inherit from type, we get a TypeError: nonempty
    # __slots__ not supported for subtype of type
    #################################################################
    # commented out: "multiple bases have instance lay-out conflict"
    # presumably caused by presence of __slots__
    # __slots__ = ['_value', ]

    # should default precede value?  if a value is assigned, isn't that
    # a default?  In fact shouldn't the parameter list end with
    #   value=default?
    def __init__(self, value=None):
        # XXX NEED SOME VALIDATION
        # DEBUG
        print("  type of value: %s" % type(value))
        print("FieldImpl.__init__: value = %s" % value)  # .decode('utf-8'))
        # END
        self._value = value

    def __eq__(self, other):
        if other is None:
            return False
        if self is other:
            return True
        # pylint doesn't handle metaclasses well
        # pylint:disable=no-member
        if self._fname != other.fname or \
                self._field_type != other.field_type or \
                self._quantifier != other.quantifier or \
                self._field_nbr != other.field_nbr:
            return False
        # ignore defaults for now
        return True


class MetaField(type):
    """ Class used to construct Field classes. """

    # pylint: disable=unused-argument
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        """
        Allows us to pass arguments which become class attributes.
        """
        return dict(kwargs)

    # FOR kwargs:
    # pylint: disable=unused-argument
    def __new__(mcs, name, bases, namespace, **kwargs):
        # DEBUG
        # removed namespace from print
        print("\nMetaField NEW, mcs='%s',\n\tname='%s', bases='%s'" % (
            mcs, name, bases))
        sys.stdout.flush()
        # END
        return super().__new__(mcs, name, bases, namespace)

    # FOR kwargs:
    # pylint: disable=unused-argument
    def __init__(cls, name, bases, namespace, **kwargs):
        super().__init__(name, bases, namespace)

        # DEBUG without namespace
        print("MetaField INIT, cls='%s',\n\tname='%s', bases='%s'" % (
            cls, name, bases))
        sys.stdout.flush()
        # END

# -- MAKER ----------------------------------------------------------


def make_field_class(dotted_msg_name, field_spec):
    """ Factory for field classes. """

    if dotted_msg_name is None:
        raise FieldzError('null message name')
    if field_spec is None:
        raise FieldzError('null field spec')
    qual_name = '%s.%s' % (dotted_msg_name, field_spec.fname)
    # DEBUG
    print('MAKE_FIELD_CLASS for %s' % qual_name)
    # END
    if qual_name in FIELD_CLS_BY_Q_NAME:
        return FIELD_CLS_BY_Q_NAME[qual_name]

    # We want an attribute and a property for each field_spec attr.
    # This needs to be elaborated as appropriate to deal with the
    # 18 or so field types.

    # _field_nbr = property(my_field_nbr)
    # _quantifier = property(my_quantitier)
    _value = property(my_value_getter, my_value_setter)

#   class M(metaclass=MetaField,
#       _name=field_spec.fname,
#       # PROBLEM: THIS IS A SECOND USE OF THE ATTRIBUTE 'name'
#       # name=property(myName),
#       dummy2=0,
#       _fType=field_spec.fTypeNdx,
#       fType=property(myFType),
#       _quantifier=field_spec.quantifier,
#       quantifier=_quantifier,
#       _fieldNbr=field_spec.fieldNbr,
#       fieldNbr=_field_nbr,
#       _default=field_spec.default,
#       default=property(myDefault),
#       value=_value,
#       dummy=0):
#       pass

    # pylint: disable=too-few-public-methods
    class Field(FieldImpl, metaclass=MetaField,
                fname=field_spec.fname,
                field_type=field_spec.field_type,   # an enum member
                quantifier=field_spec.quantifier,
                field_nbr=field_spec.field_nbr,
                default=field_spec.default,
                value=_value):
        """ Class used to construct field classes. """
        pass
    # ----------------------------
    # possibly some more fiddling ...
    # ----------------------------

    FIELD_CLS_BY_Q_NAME[qual_name] = Field
    return Field
