# fieldz/fieldTypes.py

# import sys

# from fieldz.enum import SimpleEnumWithRepr
#
# #@singleton
# class FieldTypes(SimpleEnumWithRepr):
#
#     def __init__(self):
#         super(FieldTypes, self).__init__( [ \
#             # FIELDS IMPLEMENTED USING VARINTS --
#             ('_V_BOOL', 'vBool'),
#             ('_V_ENUM', 'vEnum'),
#             # -------------------------------------------------------
#             # NEXT PAIR HAVE BEEN DROPPED, perhaps foolishly; IF SE
#             # ARE ADDED BACK IN, PUT THEM IN THEIR CORRECT ORDER
#             #           ('_V_INT32',    'vInt32'),  ('_V_INT64',    'vInt64'),
#             # -------------------------------------------------------
#             ('_V_UINT32', 'vuInt32'),
#             ('_V_SINT32', 'vsInt32'),
#             ('_V_UINT64', 'vuInt64'),
#             ('_V_SINT64', 'vsInt64'),
#             # IMPLEMENTED USING B32 -------------
#             ('_F_UINT32', 'fuInt32'),
#             ('_F_SINT32', 'fsInt32'),
#             ('_F_FLOAT', 'fFloat'),
#             # IMPLEMENTED USING B64 -------------
#             ('_F_UINT64', 'fuInt64'),
#             ('_F_SINT64', 'fsInt64'),
#             ('_F_DOUBLE', 'fDouble'),
#             # IMPLEMENTED USING LEN_PLUS --------
#             ('_L_strFormING', 'lString'),
#             ('_L_BYTES', 'lBytes'),
#             ('_L_MSG', 'lMsg'),
#             # OTHER FIXED LENGTH BYTE SEQUENCES -
#             ('_F_BYTES16', 'fBytes16'),
#             ('_F_BYTES20', 'fBytes20'),
#             ('_F_BYTES32', 'fBytes32'),
#         ])

from enum import IntEnum

# XXX supposedly these should be 1-based


class FieldTypes(IntEnum):
    _V_BOOL = 0
    _V_ENUM = 1
    _V_INT32 = 2
    _V_INT64 = 3
    _V_UINT32 = 4       # skipped in the original version
    _V_SINT32 = 5       # skipped in the original version
    _V_UINT64 = 6
    _V_SINT64 = 7
    _F_UINT32 = 8
    _F_SINT32 = 9
    _F_FLOAT = 10
    _F_UINT64 = 11
    _F_SINT64 = 12
    _F_DOUBLE = 13
    _L_STRING = 14
    _L_BYTES = 15
    _L_MSG = 16
    _F_BYTES16 = 17
    _F_BYTES20 = 18
    # XXX next two must be identical
    _F_BYTES32 = 19
    MAX_NDX = 19


class FieldStr(object):

    _strForm = [
        'vBool',
        'vEnum',
        'vInt32',
        'vInt64',
        'vuInt32',
        'vsInt32',
        'vuInt64',
        'vsInt64',
        'fuInt32',
        'fsInt32',
        'fFloat',
        'fuInt64',
        'fsInt64',
        'fDouble',
        'lString',
        'lBytes',
        'lMsg',
        'fBytes16',
        'fBytes20',
        'fBytes32',
    ]

    @classmethod
    def asStr(cls, n):
        return FieldStr._strForm[n]

    def __init__(self):
        self._str2ndx = {}
        for _type in FieldTypes:
            self._str2ndx[FieldStr._strForm[_type]] = _type

    def ndx(self, s):
        return self._str2ndx[s]


# sys.modules[__name__] = FieldTypes
