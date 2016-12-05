# fieldz/fieldTypes.py

""" Define symbols representing types of binary fields. """

# import sys

# from fieldz.enum import SimpleEnumWithRepr
#
# #@singleton
# class FieldTypes(SimpleEnumWithRepr):
#
#     def __init__(self):
#         super(FieldTypes, self).__init__( [ \
#             # FIELDS IMPLEMENTED USING VARINTS --
#             ('V_BOOL', 'vBool'),
#             ('V_ENUM', 'vEnum'),
#             # -------------------------------------------------------
#             # NEXT PAIR HAVE BEEN DROPPED, perhaps foolishly; IF SE
#             # ARE ADDED BACK IN, PUT THEM IN THEIR CORRECT ORDER
#             #           ('V_INT32',    'vint32'),  ('_V_INT64',    'vint64'),
#             # -------------------------------------------------------
#             ('V_UINT32', 'vuint32'),
#             ('V_SINT32', 'vsint32'),
#             ('V_UINT64', 'vuint64'),
#             ('V_SINT64', 'vsint64'),
#             # IMPLEMENTED USING B32 -------------
#             ('F_UINT32', 'fuint32'),
#             ('F_SINT32', 'fsint32'),
#             ('F_FLOAT', 'ffloat'),
#             # IMPLEMENTED USING B64 -------------
#             ('F_UINT64', 'fuint64'),
#             ('F_SINT64', 'fsint64'),
#             ('F_DOUBLE', 'fdouble'),
#             # IMPLEMENTED USING LENPLUS --------
#             ('L_strFormING', 'lstring'),
#             ('L_BYTES', 'lbytes'),
#             ('L_MSG', 'lmsg'),
#             # OTHER FIXED LENGTH BYTE SEQUENCES -
#             ('F_BYTES16', 'fbytes16'),
#             ('F_BYTES20', 'fbytes20'),
#             ('F_BYTES32', 'fbytes32'),
#         ])

from enum import IntEnum


class FieldTypes(IntEnum):
    """
    Enumeration representing types of binary fields.

    SHOULD THESE BE 1-BASED?
    """

    V_BOOL = 0
    V_ENUM = 1
    V_INT32 = 2
    V_INT64 = 3
    V_UINT32 = 4       # skipped in the original version
    V_SINT32 = 5       # skipped in the original version
    V_UINT64 = 6
    V_SINT64 = 7
    F_UINT32 = 8
    F_SINT32 = 9
    F_FLOAT = 10
    F_UINT64 = 11
    F_SINT64 = 12
    F_DOUBLE = 13
    L_STRING = 14
    L_BYTES = 15
    L_MSG = 16
    F_BYTES16 = 17
    F_BYTES20 = 18
    F_BYTES32 = 19
    MAX_NDX = 19


class FieldStr(object):
    """ Strings naming types of binary fields. """

    _str_form = [
        'vbool',
        'venum',
        'vint32',
        'vint64',
        'vuint32',
        'vsint32',
        'vuint64',
        'vsint64',
        'fuint32',
        'fsint32',
        'ffloat',
        'fuint64',
        'fsint64',
        'fdouble',
        'lstring',
        'lbytes',
        'lmsg',
        'fbytes16',
        'fbytes20',
        'fbytes32',
    ]
    _str2ndx = {}
    for _type in FieldTypes:
        _str2ndx[_str_form[_type]] = _type

    @classmethod
    def as_str(cls, ndx):
        """ Given the index of a field type, return its string form. """
        return FieldStr._str_form[ndx]

    def __init__(self):
        pass

    @classmethod
    def ndx(cls, string):
        """ Given the string form of a field type, return its index. """
        return FieldStr._str2ndx[string]


# sys.modules[__name__] = FieldTypes
