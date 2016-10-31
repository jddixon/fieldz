# fieldz/core.py

__all__ = ['SimpleEnum', 'SimpleEnumWithRepr', ]

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
        for ndx in range(len(symbols)):
            # XXX we could enforce capitalization here
            self.__dict__[symbols[ndx]] = ndx
        self._max_ndx_ = len(symbols)

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
        if sym not in self.__dict__:
            self.__dict__[sym] = value
        else:
            raise TypeError(
                'attempt to change value of constant ' + sym)

    @property
    def max_ndx(self):
        """ return the highest index number currently in use """
        return self._max_ndx_

# -------------------------------------------------------------------


class SimpleEnumWithRepr(object):
    """ Should certainly be a singleton """

    def __setattr__(self, sym, value):
        """ instance variables may be set but never reset """
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
        was ('PLUS', '+'), then Q.PLUS would have the constant value 3 and
        its representation, Q.name(Q.PLUS), would be '+'.
        """

        self._str_form = []            # list of string representations
        self._str2ndx = {}             # maps string strForm to ints
        for ndx, pair in enumerate(pairs):
            sym = pair[0]           # a string
            self.__setattr__(sym, ndx)          # the corresponding int value
            self._str_form.append(pair[1])
            self._str2ndx[pair[1]] = ndx

        self._max_type_ = self.__dict__[pairs[-1][0]]

    def as_str(self, ndx):
        if ndx is None or ndx < 0 or self._max_type_ < ndx:
            raise ValueError('symbol index out of range: %s' % str(ndx))
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
        return self._max_type_
