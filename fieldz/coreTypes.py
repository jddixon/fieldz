# corez/coreTypes.py

import sys
from fieldz.enum import SimpleEnumWithRepr

#@singleton


class CoreTypes(SimpleEnumWithRepr):

    def __init__(self):
        super(CoreTypes, self).__init__([
            ('_ENUM_PAIR_SPEC', 'EnumPairSpec'),
            ('_ENUM_SPEC', 'EnumSpec'),
            ('_FIELD_SPEC', 'FieldSpec'),
            ('_MSG_SPEC', 'MsgSpec'),
            ('_SEQ_SPEC', 'SeqSpec'),
            ('_PROTO_SPEC', 'ProtoSpec'),
        ])

sys.modules[__name__] = CoreTypes()
