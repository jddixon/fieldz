# fieldz/core.py

__all__ = [ \
    # classes being played around with
    'SimpleEnum', 'SimpleEnumWithRepr',
]

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
        for i in range(len(symbols)):
            # XXX we could enforce capitalization here
            self.__dict__[symbols[i]] = i
        self._MAX_NDX = i

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
        if sym not in self.__dict__:
            self.__dict__[sym] = value
        else:
            raise self.FieldTypeError(
                'attempt to change value of constant ' + sym)

    @property
    def maxNdx(self):
        return self._MAX_NDX

# -------------------------------------------------------------------


class SimpleEnumWithRepr(object):

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
        if sym not in self.__dict__:
            self.__dict__[sym] = value
        else:
            raise RuntimeError('attempt to change value of constant ' + sym)

    def __init__(self, pairs):
        """
        pairs is a list of string pairs.  The first string in each pair
        will become something very close to a constant.  Conventionally
        this is capitalized.  The second string represents its name, its
        string representation in the programming context.  If the subclass
        passing the list of pairs was Q and the third pair (zero-based)
        was ('PLUS', '+'), then Q.PLUS would have the constant value 3 and
        its representation, Q.name(Q.PLUS), would be '+'.
        """

        self._strForm = []            # list of string representations
        self._str2ndx = {}             # maps string strForm to ints
        for i in range(len(pairs)):
            pair = pairs[i]
            sym = pair[0]              # a string
            self.__dict__[sym] = i      # the corresponding int value
            self._strForm.append(pair[1])
            self._str2ndx[pair[1]] = i

        self._MAX_TYPE = self.__dict__[pairs[-1][0]]

    def asStr(self, n):
        if n is None or n < 0 or self._MAX_TYPE < n:
            raise ValueError('symbol index out of range: %s' % str(n))
        return self._strForm[n]

    def ndx(self, s):
        """
        Maps a string representation to the unique integer value associated
        with the corresponding symbol.
        """
        if s is None or not s in self._str2ndx:
            print("DEBUG: symbol '%s' not in enum" % s)
            return None
        else:
            return self._str2ndx[s]

    @property
    def maxNdx(self):
        return self._MAX_TYPE
