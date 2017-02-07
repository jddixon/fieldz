# fieldz/enum.py

"""
Enumeration types.
"""

from enum import Enum, IntEnum
import warnings

from fieldz import FieldzError


__all__ = ['CoreTypes', 'Quants',
           # DEPRECATED -----------------------------------
           'SimpleEnum', 'SimpleEnumWithRepr', ]
# END DEPRECATED ------------------------------


# CORE TYPES ========================================================

# pylint: disable=invalid-name
CoreTypes = IntEnum('CoreTypes', [
    'ENUM_PAIR_SPEC', 'ENUM_SPEC', 'FIELD_SPEC',
    'MSG_SPEC', 'SEQ_SPEC', 'PROTO_SPEC', ], start=0)

_CT_SYMBOLS = [
    'EnumPairSpec', 'EnumSpec', 'FieldSpec',
    'MsgSpec', 'SeqSpec', 'ProtoSpec', ]


@property
def _ct_sym(self):
    """ Return the symbol associated with this member. """
    return _CT_SYMBOLS[self.value]

CoreTypes.sym = _ct_sym       # add the method to the class

_CT_NDX = {}
# pylint: disable=not-an-iterable
for _ in CoreTypes:
    """ Map the field type's symbol back to the member """
    _CT_NDX[_.sym] = _


@classmethod
# pylint: disable=unused-argument
def _from_sym(cls, symbol):
    """ Given a symbol, return the corresponding member. """
    return _CT_NDX[symbol]

CoreTypes.from_sym = _from_sym

# QUANTIFIERS =======================================================

# Quantifiers, specifying how many members may be present.
# pylint: disable=invalid-name
Quants = IntEnum('Quants', ['REQUIRED', 'OPTIONAL', 'STAR', 'PLUS'], start=0)

_Q_SYMBOLS = ['', '?', '*', '+', ]


@property
def _q_sym(self):
    """ Return the symbol associated with this smember. """
    return _Q_SYMBOLS[self.value]

Quants.sym = _q_sym

# DEPRECATED ========================================================

"""
Enumeration types.

These were specified for Python 2.7, and ARE NOT SUITABLE for Python 3.
"""

# DOESN'T WORK.
# def singleton(cls):
#    """ for use with @singleton """
#
#    # possibly add this to module strFormpace at runtime, building a
#    # variable name like __${cls.name}_instance__
#    _instance = None
#    def getinstance():
#        if _instance is None:
#            # this raises a TypeError: line 9 in fieldTypes.py in __init__,
#            # super(FieldTypes,self).__init__(
#            # TyperError: must be type, not function(
#            _instance = cls()
#        return _instance
#    return getinstance


class SimpleEnum(object):
    """
    Define a list of symbols as resolving to their index value, so
    that if E is a subclass defining a list of symbols A,B,C, then
    E.B is a constant with value 1.
    """

    def __init__(self, symbols):
        warnings.warn("SimpleEnum", DeprecationWarning)
        for ndx, symbol in enumerate(symbols):
            # XXX we could enforce capitalization here
            self.__dict__[symbol] = ndx
        self._max_ndx_ = len(symbols)

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
        warnings.warn("SimpleEnum.__setattr__", DeprecationWarning)
        if sym not in self.__dict__:
            self.__dict__[sym] = value
        else:
            raise TypeError(
                'attempt to change value of constant ' + sym)

    @property
    def max_ndx(self):
        """ return the highest index number currently in use """
        warnings.warn("SimpleEnum.max_ndx", DeprecationWarning)
        return self._max_ndx_

# -------------------------------------------------------------------


class SimpleEnumWithRepr(object):
    """ Should certainly be a singleton """

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
        warnings.warn("SimpleEnumWithRepr", DeprecationWarning)
        if sym not in self.__dict__:
            super().__setattr__(sym, value)
        else:
            raise RuntimeError('attempt to change value of constant ' + sym)

    def __init__(self, pairs):
        """
        pairs is a list of string pairs.  The first string in each pair
        will become something very close to a constant.  Conventionally
        this is capitalized.  The second string represents its name, its
        string representation in the programming context.  If the subclass
        passing the list of pairs was Q and the third pair (zero-based)
        was ('PLUS', '+'), then Quants.PLUS would have the constant value 3 and
        its representation, Quants.name(Quants.PLUS), would be '+'.
        """

        warnings.warn("SimpleEnumWithRepr", DeprecationWarning)
        self._str_form = []            # list of string representations
        self._str2ndx = {}             # maps string strForm to ints
        for ndx, pair in enumerate(pairs):
            sym = pair[0]           # a string
            self.__setattr__(sym, ndx)          # the corresponding int value
            self._str_form.append(pair[1])
            self._str2ndx[pair[1]] = ndx

        self._max_type_ = self.__dict__[pairs[-1][0]]

    def as_str(self, ndx):
        """ Return the string form of the Nth enumerate. """

        warnings.warn("SimpleEnumWithRepr:as_str", DeprecationWarning)
        if ndx is None or ndx < 0 or self._max_type_ < ndx:
            raise FieldzError('symbol index out of range: %s' % str(ndx))
        return self._str_form[ndx]

#   def ndx(self, string):
#       """
#       Maps a string representation to the unique integer value associated
#       with the corresponding symbol.
#       """
#       if string is None or not string in self._str2ndx:
#           print("DEBUG: symbol '%s' not in enum" % string)
#           return None
#       else:
#           return self._str2ndx[string]

    @property
    def max_ndx(self):
        """ Return the maximum index assigned to an enumerate. """
        warnings.warn("SimpleEnumWithRepr:max_ndx", DeprecationWarning)
        return self._max_type_

# END DEPRECATED ====================================================
