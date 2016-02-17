# fieldz/enumSpec.py
import sys

from fieldz.enum import SimpleEnum

# This is actually another intertwined pair of enums: we want 
# these values to map to  ['', '?', '*', '+'] 

class QEnum(SimpleEnum):
    def __init__(self):
        super(QEnum, self).__init__(['REQUIRED', 'OPTIONAL', 'STAR', 'PLUS'])

# This allows us to import a reference to the class instance.
sys.modules[__name__] = QEnum()
