# fieldz/enumSpec.py

""" Enumeration of quantifiers. """

import sys

from fieldz.enum import SimpleEnum


class QEnum(SimpleEnum):
    """
    This is actually another intertwined pair of enums: we want
    these values to map to  ['', '?', '*', '+'].
    """

    def __init__(self):
        super(QEnum, self).__init__(['REQUIRED', 'OPTIONAL', 'STAR', 'PLUS'])

# This allows us to import a reference to the class instance.
sys.modules[__name__] = QEnum()
