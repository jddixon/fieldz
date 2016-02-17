# fieldz/fieldTypes.py

import sys
#from fieldz.core import singleton, SimpleEnumWithRepr
from fieldz.enum import SimpleEnumWithRepr

#@singleton
class FieldTypes(SimpleEnumWithRepr):
    def __init__(self):
        super(FieldTypes,self).__init__( [ \
            # FIELDS IMPLEMENTED USING VARINTS --
            ('_V_BOOL',     'vBool'),   
            ('_V_ENUM',     'vEnum'),
            # -------------------------------------------------------
            # NEXT PAIR HAVE BEEN DROPPED, perhaps foolishly; IF THESE
            # ARE ADDED BACK IN, PUT THEM IN THEIR CORRECT ORDER
#           ('_V_INT32',    'vInt32'),  ('_V_INT64',    'vInt64'),
            # -------------------------------------------------------
            ('_V_UINT32',   'vuInt32'), 
            ('_V_SINT32',   'vsInt32'), 
            ('_V_UINT64',   'vuInt64'),
            ('_V_SINT64',   'vsInt64'),
            # IMPLEMENTED USING B32 -------------
            ('_F_UINT32',   'fuInt32'), 
            ('_F_SINT32',   'fsInt32'), 
            ('_F_FLOAT',    'fFloat'),
            # IMPLEMENTED USING B64 -------------
            ('_F_UINT64',   'fuInt64'), 
            ('_F_SINT64',   'fsInt64'), 
            ('_F_DOUBLE',   'fDouble'),
            # IMPLEMENTED USING LEN_PLUS --------
            ('_L_STRING',   'lString'), 
            ('_L_BYTES',    'lBytes'),
            ('_L_MSG',      'lMsg'),
            # OTHER FIXED LENGTH BYTE SEQUENCES -
            ('_F_BYTES16',  'fBytes16'),
            ('_F_BYTES20',  'fBytes20'),
            ('_F_BYTES32',  'fBytes32'),
        ])

sys.modules[__name__] = FieldTypes()
