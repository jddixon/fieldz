# corez/coreTypes.py

""" The enumeration of specification types. """

#import sys
from fieldz.enum import SimpleEnumWithRepr

#@singleton


class CoreTypes(SimpleEnumWithRepr):

    def __init__(self):
        super(CoreTypes, self).__init__([
            ('ENUM_PAIR_SPEC', 'EnumPairSpec'),
            ('ENUM_SPEC', 'EnumSpec'),
            ('FIELD_SPEC', 'FieldSpec'),
            ('MSG_SPEC', 'MsgSpec'),
            ('SEQ_SPEC', 'SeqSpec'),
            ('PROTO_SPEC', 'ProtoSpec'),
        ])

# sys.modules[__name__] = CoreTypes()
