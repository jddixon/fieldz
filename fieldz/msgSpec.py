# fieldz/msgSpec.py

import re
import sys

from fieldz.raw import *
from fieldz.typed import *

import fieldz.fieldTypes as F
import fieldz.coreTypes as C

__all__ = [  \
    # constants, so to speak: quantifiers
    'Q_REQUIRED',   # no quantifier, so one and only one such field
    'Q_OPTIONAL',   # ?: either zero or one instance of the field
    'Q_STAR',       # *: zero or more instances of the field allowed
    'Q_PLUS',       # +: one or more instances of the field
    'Q_NAMES',      # list of the four above
    # methods
    'qName', 'validateSimpleName', 'validateDottedName',

    # class-level
    'cPutFuncs', 'cGetFuncs', 'cLenFuncs',

    'enumPairSpecPutter', 'enumSpecPutter', 'fieldSpecPutter',
    'msgSpecPutter', 'seqSpecPutter', 'protoSpecPutter',

    'enumPairSpecGetter', 'enumSpecGetter', 'fieldSpecGetter',
    'msgSpecGetter', 'seqSpecGetter', 'protoSpecGetter',

    'enumPairSpecLen', 'enumSpecLen', 'fieldSpecLen',
    'msgSpecLen', 'seqSpecLen', 'protoSpecLen',

    # classes
    'EnumPairSpec', 'EnumSpec', 'FieldSpec',
    'MsgSpec', 'ProtoSpec',
    'SeqSpec',
]

Q_REQUIRED = 0
Q_OPTIONAL = 1
Q_STAR = 2
Q_PLUS = 3

Q_NAMES = ['', '?', '*', '+', ]


def qName(n):
    if n < 0 or n >= len(Q_NAMES):
        raise ValueError('does not map to a valid quantifier: %s' % str(n))
    return Q_NAMES[n]

# base names, forming part of a larger pattern
_VALID_NAME_PAT = "[a-zA-Z_][a-zA-Z_0-9]*"
_VALID_NAME_RE = re.compile(_VALID_NAME_PAT)

# just base names; match will fail if any further characters follow
_VALID_SIMPLE_NAME_PAT = _VALID_NAME_PAT + '$'
_VALID_SIMPLE_NAME_RE = re.compile(_VALID_SIMPLE_NAME_PAT)


def validateSimpleName(s):
    m = _VALID_SIMPLE_NAME_RE.match(s)
    if m is None:
        raise RuntimeError("invalid simple name '%s'" % s)

# both protocol names and field names can be qualified
_VALID_DOTTED_NAME_PAT = _VALID_NAME_PAT + '(\.' + _VALID_NAME_PAT + ')*$'
_VALID_DOTTED_NAME_RE = re.compile(_VALID_DOTTED_NAME_PAT)


def validateDottedName(s):
    m = _VALID_DOTTED_NAME_RE.match(s)
    if m is None:
        raise RuntimeError("invalid (optionally dotted) name %s'" % s)


# -- CLASSES --------------------------------------------------------
class EnumPairSpec(object):
    __slots__ = ['_symbol', '_value', ]

    def __init__(self, symbol, value):
        validateSimpleName(symbol)
        self._symbol = symbol
        self._value = int(value)

    @property
    def symbol(self): return self._symbol

    @property
    def value(self): return self._value

    def __eq__(self, other):
        if other is None or not isinstance(other, EnumPairSpec):
            print('XXX None or not EnumPairSpec')
            return False
        if (self._symbol != other._symbol) or (self._value != other._value):
            print('XXX symbol or value differs')
            return False
#       print 'XXX pairs match'
#       print "  my    self:  %s" % self
#       print "  other other: %s" % other
        return True

    def indentedStr(self, indent='', step=''):
        return "%s%s = %d\n" % (indent, self._symbol, self._value)

    def __str__(self):
        """ return a usable representation of the EnumPairSpec """
        return self.indentedStr('    ')

    def __repr__(self):
        """ return the EnumPairSpec in today's notion of the canonical form """
        return self.indentedStr(' ')


class EnumSpec(object):
    """
    For our purposes an enum is a named list of simple names (names
    containing no delimiters)` and a map from such names to their
    non-negative integer values.
    """
    __slots__ = ['_name', '_pairs', '_sym2pair', ]

    def __init__(self, name, pairs):
        """pairs are EnumPairSpecs """
        validateDottedName(name)
        self._name = name
        if pairs is None:
            raise ValueError('null list of enum pairs')
        if len(pairs) == 0:
            raise ValueError('empty list of enum pairs')
        self._pairs = []
        self._sym2pair = {}
        for pair in pairs:
            sym = pair.symbol
            val = pair.value
            if sym in self._sym2pair:
                raise ValueError("already in EnumSpec: '%s'" % sym)
            self._pairs.append(pair)
            self._sym2pair[sym] = pair

    @classmethod
    def create(cls, name, pairs):
        """pairs are 2-tuples, (symbol, value), where value is uInt16 """
        validateDottedName(name)
        if pairs is None:
            raise ValueError('null list of enum pairs')
        if len(pairs) == 0:
            raise ValueError('empty list of enum pairs')

        _pairs = []
        for pair in pairs:
            sym = pair[0]
            val = pair[1]
            p = EnumPairSpec(sym, val)
            _pairs.append(p)
        return EnumSpec(name, _pairs)

    def value(self, s):
        """ map a name to the corresponding value """
        return self._sym2pair[s].value

    @property
    def name(self): return self._name

    # def pair(self, k):
    def __getitem__(self, k):
        return self._pairs[k]

    def __len__(self): return len(self._pairs)

    def __eq__(self, other):
        # print "ENUM_SPEC COMPARISON"
        if other is None or not isinstance(other, EnumSpec):
            return False
        if other is self:
            return True
        if other._name != self._name:
            return False
        if len(self._pairs) != len(other._pairs):
            return False

        # print "  ENUM LENGTHS match"
        for i in range(self.__len__()):
            # if self[i] != other[i]:
            if self[i].symbol != other[i].symbol or \
                    self[i].value != other[i].value:
                print("ENUM_PAIR_SPECS DIFFER:")
                print("  my    pair %u: %s" % (i, self[i]))
                print("  other pair %u: %s" % (i, other[i]))
                return False
        return True

    def indentedStr(self, indent='', step=''):
        # DEBUG
        print("EnumSpec.indentedStr <-------------------")
        # END
        s = []
        s.append('%senum %s\n' % (indent, self.name))
        for pair in self._pairs:
            s.append(pair.indentedStr(indent + step, step))
        return ''.join(s)

    def __str__(self):
        """ return a usable representation of the EnumSpec """
        return self.indentedStr('', '    ')

    def __repr__(self):
        """ return the EnumSpec in today's notion of the canonical form """
        return self.indentedStr('', ' ')


class FieldSpec(object):
    __slots__ = ['_reg',
                 '_name', '_type', '_quantifier', '_fieldNbr', '_default', ]

    def __eq__(self, other):
        if other is None or not isinstance(other, FieldSpec):
            return False
        # using == in the next line causes infinite recursion
        if other is self:
            return True
        if other._name != self._name:
            print("FIELD_SPEC NAMES DIFFER")
            return False
        # ignore this for now; cloned fields have different reges
#       if other._reg != self._reg:
#           print "FIELD_SPEC REGES DIFFER"
#           return False
        if other._type != self._type:
            print("FIELD_SPEC TYPES DIFFER")
            return False
        if other._quantifier != self._quantifier:
            print("FIELD_SPEC QUANTIFIERS DIFFER")
            return False
        if self._fieldNbr:
            if other._fieldNbr is None:
                print("OTHER FIELD_SPEC HAS NO FIELD NBR")
                return False
            if self._fieldNbr != other._fieldNbr:
                print("FIELD_SPEC FIELD NBRS DIFFER")
                return False

        # XXX IGNORE DEFAULTS FOR NOW

        return True

    def __init__(self, reg, name, fType, quantifier=Q_REQUIRED,
                 fieldNbr=-1, default=None):
        if reg is None:
            raise ValueError('reg must be specified')
        self._reg = reg

        # -- name ---------------------------------------------------
        if name is None or len(name) == 0:
            raise ValueError('no field name specified')

        # DEBUG
        # print("FieldSpec.__init__: name '%s' is of type %s" % (
        #    name, type(name)))
        # END
        validateDottedName(name)
        self._name = name

        # -- fType --------------------------------------------------
        # XXX RANGE CHECK TEMPORARILY DISABLED -
#       if fType < 0 or fType > F.maxNdx:
#           raise ValueError("invalid fType '%s'" % str(fType))
        self._type = fType

        # -- quantifier ---------------------------------------------
        # XXX BAD RANGE CHECK
        if quantifier < 0 or quantifier > Q_PLUS:
            raise ValueError("invalid quantifier '%s'" % str(quantifier))
        self._quantifier = quantifier

        # -- fieldNbr -----------------------------------------------
        self._fieldNbr = int(fieldNbr)

        # -- default ------------------------------------------------
        # if default is None, could provide a default appropriate for the type
        # XXXif we are going to support a default value, it needs to be
        #   validated
        # XXX STUB
        if default is not None:
            raise NotImplementedError('default for FieldSpec')
        self._default = default

    @property
    def name(self): return self._name

    # XXX return a string value
    @property
    def fTypeName(self):
        if 0 <= self._type and self._type <= F.maxNdx:
            return F.asStr(self._type)
        regID = self._reg.regID2Name(self._type)
        if regID is None:
            # XXX parent must search upwards if not found
            regID = self._reg.parent.regID2Name(self._type)
        return regID

    # XXX return a number
    @property
    def fTypeNdx(self): return self._type

    @property
    def quantifier(self): return self._quantifier
    #def quantifier(self):   return Q_NAMES[self._quantifier]

    @property
    def fieldNbr(self):
        return self._fieldNbr

    @fieldNbr.setter
    def fieldNbr(self, value):
        v = int(value)
        if v < 0:
            raise ValueError('field number may not be negative')
        self._fieldNbr = v

    @property
    def default(self): return self._default

    def indentedStr(self, indent, step):
        s = []
        s.append('%s%s ' % (indent, self._name))

        tName = self.fTypeName
        if self._quantifier != Q_REQUIRED:
            tName += qName(self._quantifier)
        s.append('%s ' % tName)               # at least one space

        if self._fieldNbr is not None:
            s.append('@%d ' % self._fieldNbr)  # again, at least one space

        #========================
        # XXX default not handled
        #========================
        s.append('\n')

        return '' . join(s)

    def __str__(self):
        """ return a prettier representation of the FieldSpec """
        return self.indentedStr('', '    ')

    def __repr__(self):
        """
        Return the FieldSpec in today's notion of the canonical form.
        This doesn't have to be pretty, just absolutely clear and
        unambiguous.
        """
        return self.indentedStr('', ' ')


class SeqSpec(object):
    """

    """

    def __init__(self):
        pass
        # XXX STUB

    def indentedStr(self, indent, step):
        raise NotImplementedError('indentedStr for SeqSpec')

    def __str__(self):
        return self.indentedStr('', '    ')

    def __repr__(self):
        return self.indentedStr('', ' ')                # GEEP

# SUPER SPECS =======================================================


class SuperSpec(object):
    __slots__ = ['_name', '_parent', '_myReg', '_enums', '_msgs',
                 '_msgsByName', '_msgNameNdx', '_nextMsg',
                 ]

    def __init__(self, name, reg, parent=None):
        if name is None:
            raise ValueError('missing protocol name')
        validateDottedName(name)
        self._name = name

        if reg is None:
            raise ValueError('proto reg must be specified')
        self._myReg = reg

        self._parent = parent

        self._enums = []
        self._msgs = []
        self._msgsByName = {}
        self._msgNameNdx = {}    # map name to index
        self._nextMsg = 0

    @property
    def name(self): return self._name

    @property
    def parent(self): return self._parent             # FOO

    @property
    def reg(self): return self._myReg          # this protocol's reg

    # XXX we should make iterators available instead
    @property
    def enums(self): return self._enums

    @property
    def msgs(self): return self._msgs

    def addEnum(self, e):
        # should validate AND check for uniqueness

        # DEBUG
        name = e.name
        print("ADDING ENUM %s TO SUPER_SPEC" % name)
        # END

        # WORKING HERE
        self._enums.append(e)

    def addMsg(self, m):
        name = m.name
        # XXX This forbids shadowing of the name in the parent but
        #     not further up the tree
        if name in self._msgsByName or (self.parent is not None
                                        and name in self.parent._msgsByName):
            raise RuntimeError("name '%s' is already in use" % name)
        print("ADDING MSG %s TO PROTO SPEC LIST" % name)         # DEBUG
        self._msgs.append(m)
        self._msgsByName[name] = m                             # FOO
        self._msgNameNdx[name] = self._nextMsg
        self._nextMsg += 1

    def getMsgSpec(self, name):
        """ given a name, returns the corresponding msgSpec """
        return self._msgsByName[name]

    def msgNameIndex(self, name):
        """ given a name, returns its index """
        return self._msgNameNdx[name]

    # XXX USELESS IN ITS PRESENT STATE ------------------------------
    def getRegIDForName(self, name):
        """
        If the name is in use, raise an exception.  Otherwise, return
        the next free regID.
        """

        # THIS LOGIC DOESN'T PERMIT FULLY RECURSIVE STRUCTURE

        # XXX THIS IS NONSENSE: there is no MsgSpec._byName

        if name in self._msgsByName or name in self.parent._msgsByName:
            raise RuntimeError("name '%s' is already in use" % name)

        # XXX STUB XXX GET THE NEXT FREE regID
    # END USELESS


class ProtoSpec(SuperSpec):
    """
    A protocol is a set of message types, enumerations, and acceptable
    message sequences.  It is essential for our purposes that any
    protocol can be constructed dynamically from its wire serialization.
    """

    __slots__ = ['_seqs', ]

    def __init__(self, name, reg):
        super(ProtoSpec, self).__init__(name, reg)  # parent is None
        self._seqs = []                # XXX NOT YET SUPPORTED

    @property
    def seqs(self): return self._seqs

    def addSeq(self, s):
        # should validate AND check for uniqueness
        self._seqs.append(s)

    # MOVE MOST OF THIS INTO SuperSpec ##############################
    def __eq__(self, other):
        if other is None:
            return False
        if other is self:
            return True
        if self._name != other._name:
            return False

        #------------------------------------------------------------
        # XXX THESE THREE SETS OF TESTS NEED REVISITING, because
        # if any of {self,other}._{enums,msgs,seqs} is None, it
        # should be treated as though it were [].
        # I have changed the constructor to automatically replace
        # None with [].  Does this solve the problem?
        #------------------------------------------------------------
        if self._enums is None:
            if other._enums is not None:
                return False
        else:
            if other._enums is None:
                return False
            n = len(self._enums)
            if n != len(other._enums):
                return False
            for i in range(n):
                # XXX DOES NOT WORK AS EXPECTED
                # if self._enums[i] != other._enums[i]:   return False
                if not self._enums[i].__eq__(other._enums[i]):
                    return False

        if self._msgs is None:
            if other._msgs is not None:
                return False
        else:
            if other._msgs is None:
                return False
            n = len(self._msgs)
            if n != len(other._msgs):
                return False
            for i in range(n):
                if not self._msgs[i].__eq__(other._msgs[i]):
                    return False

        if self._seqs is None:
            if other._seqs is not None:
                return False
        else:
            if other._seqs is None:
                return False
            n = len(self._seqs)
            if n != len(other._seqs):
                return False
            for i in range(n):
                if self._seqs[i] != other._seqs[i]:
                    return False

        return True

    def indentedStr(self, indent='', step=' '):
        s = []
        s.append("%sprotocol %s\n" % (indent, self._name))
        if self._enums is not None:
            for e in self._enums:
                s.append(e.indentedStr(indent, step))
        if self._msgs is not None:
            for m in self._msgs:
                print("DEBUG: ProtoSpec SERIALIZING " + m.name)
                s.append(m.indentedStr(indent, step))
        if self._seqs is not None:
            for q in self._seqs:
                s.append(q.indentedStr(indent, step))

        return ''.join(s)

    def __str__(self):
        return self.indentedStr('', '    ')

    def __repr__(self):
        return self.indentedStr('', ' ')                        # GEEP


class MsgSpec(SuperSpec):
    """
    A message is specified as an acceptable sequence of typed fields.
    Each field has a zero-based index (field number), a name, and a type.
    Later it will have a default value.

    Serialized, a message spec begins with the name of the message,
    which is a lenPlus string; this must be either a simple name
    containing no delimiters or it may be a sequence of simple names
    separated by dots ('.').  This is followed by individual field
    specs, each of which is a lenPlus names followed by colon (':')
    followed by a fieldType.

    """
    __slots__ = ['_fields',
                 '_lastFieldNbr',           # must increase monotonically
                 'fieldNameToNdx',
                 '_fieldNdx',                    # zero-based field index
                 ]

    def __init__(self, name, parent, reg):
        if parent is None:
            raise ValueError('parent must be specified')
        name = str(name)
        validateSimpleName(name)
        super(MsgSpec, self).__init__(name, reg, parent)

        parent.addMsg(self)

        self._fields = []
        self._lastFieldNbr = -1
        self.fieldNameToNdx = {}    # XXX value?
        self._fieldNdx = 0     # zero-based index of field in MsgSpec

    def addField(self, f):
        fName = f.name
        if not isinstance(f, FieldSpec):
            raise ValueError("'%s' is not a FieldSpec!" % fName)
        if fName in self.fieldNameToNdx:
            raise KeyError("field named %s already exists" % fName)
        if f.fieldNbr < 0:
            self._lastFieldNbr += 1
            f.fieldNbr = self._lastFieldNbr
        elif f.fieldNbr <= self._lastFieldNbr:
            raise ValueError(
                "field number is %d not greater than last %d" % (
                    f.fieldNbr, self._lastFieldNbr))
        else:
            self._lastFieldNbr = f.fieldNbr
        self._fields.append(f)
        self.fieldNameToNdx[fName] = self._fieldNdx
        self._fieldNdx += 1         # so this is a count of fields

    def __len__(self): return len(self._fields)

    def __getitem__(self, k):
        """ iterates over fields of the message """
        return self._fields[k]

    def fName(self, i):
        if i < 0 or i > self.__len__():
            raise ValueError('field number out of range')
        return self._fields[i].name

    def fTypeName(self, i):
        # field numbers are zero-based
        if i < 0 or i >= self.__len__():
            raise ValueError('field number out of range')
        # XXX WRONG-ish: fType MUST be numeric; this should return
        # the string equivalent; HOWEVER, if the type is lMsg, we
        # want to return the message name ... XXX
        return self._fields[i].fTypeName

    def fTypeNdx(self, i):
        # field numbers are zero-based
        if i < 0 or i >= self.__len__():
            raise ValueError('field number out of range')

        # XXX WRONG-ish: fType MUST be numeric; this should return
        # the string equivalent; HOWEVER, if the type is lMsg, we
        # want to return the message name ... XXX
        return self._fields[i].fTypeNdx

    def fDefault(self, i):
        # field numbers are zero-based
        if i < 0 or i >= self.__len__():
            raise ValueError('field number out of range')
        return self._fields[i].default

    # -- serialization ----------------------------------------------
    def __eq__(self, other):
        if other is None or not isinstance(other, MsgSpec):
            return False
        # using == in the next line causes infinite recursion
        if other is self:
            return True
        if other._name != self._name:
            return False
        if self.__len__() == 0 or other.__len__() == 0:
            return False
        if self.__len__() != other.__len__():
            return False
        for n in range(self.__len__()):
            if not self._fields[n].__eq__(other._fields[n]):
                return False
        return True

    def indentedStr(self, indent, step):
        s = []
        # s.append( "%sprotocol %s\n\n" % (indent, self._protocol))
        s.append("%smessage %s\n" % (indent, self._name))
        if self._enums is not None:
            for e in self._enums:
                s.append(e.indentedStr(indent + step, step))
        if self._msgs is not None:
            for m in self._msgs:
                s.append(m.indentedStr(indent + step, step))
        for f in self._fields:
            s.append(f.indentedStr(indent + step, step))
        return ''.join(s)

    def __str__(self):
        """ return string representation in perhaps prettier format """
        return self.indentedStr('', '    ')

    def __repr__(self):
        """ return string representation in canonical format """
        return self.indentedStr('', ' ')                        # GEEP

# DISPATCH TABLES ===================================================

# XXX dunno why notImpl is not picked up by
#                                          from fieldz.typed import *


def notImpl(*arg): raise NotImplementedError

cPutFuncs = [notImpl] * (C.maxNdx + 1)
cGetFuncs = [notImpl] * (C.maxNdx + 1)
cLenFuncs = [notImpl] * (C.maxNdx + 1)
cPLenFuncs = [notImpl] * (C.maxNdx + 1)

# PUTTERS, GETTERS, LEN FUNCS ---------------------------------------

lStringLen = tLenFuncs[F._L_STRING]
lStringPut = tPutFuncs[F._L_STRING]
vuInt32Len = tLenFuncs[F._V_UINT32]
vuInt32Put = tPutFuncs[F._V_UINT32]
vEnumGet = tGetFuncs[F._V_ENUM]
vEnumLen = tLenFuncs[F._V_ENUM]
vEnumPut = tPutFuncs[F._V_ENUM]

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# LEN PARAMETERS MUST BE (val, n), where n is the field number
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


def enumPairSpecLen(val, n):
    """
    val is guaranteed to be a well-formed EnumPair object; this is
    the length of the spec on the wire, what is written before the spec.
    Returns the total of the encoded length of the symbol and that of
    its value.
    """
    return lStringLen(val.symbol, n) + vuInt32Len(val.value, n)


def enumPairSpecPrefixedLen(val, n):
    """
    val is guaranteed to be a well-formed EnumPair object; this is
    the length of the spec on the wire, what is written before the spec.
    So it is the total length of the header plus the length of the encoded
    byte count plus the length of the encoded enumPairSpec.
    """
    h = lengthAsVarint(fieldHdrLen(n, LEN_PLUS_TYPE))
    byteCount = enumPairSpecLen(val, n)
    return h + lengthAsVarint(byteCount) + byteCount

# val = instance of the type, n = field number


def enumPairSpecPutter(chan, val, n):
    # write the field header
    writeRawVarint(chan, fieldHdr(n, LEN_PLUS_TYPE))

    # write the byte count
    count = enumPairSpecLen(val, n)
    writeRawVarint(chan, count)
#   print "AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write field 0, the symbol
    lStringPut(chan, val.symbol, 0)
#   print "AFTER WRITING SYMBOL %s pos = %u" % ( val.symbol, pos)

    # write field 1, the value
    vuInt32Put(chan, val.value, 1)
#   print "AFTER WRITING VALUE %u pos = %u" % (val.value, pos)


def enumPairSpecGetter(chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = readRawVarint(chan)
    end = chan.position + byteCount           # XXX should use for validation

    # read field 0
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    s = readRawLenPlus(chan)
    sym = s.decode('utf-8')                   # convert bytes to str

    # read field 1
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    val = readRawVarint(chan)

    # construct the EnumPairSpec object from field values
    obj = EnumPairSpec(sym, val)
    return obj

cLenFuncs[C._ENUM_PAIR_SPEC] = enumPairSpecLen
cPLenFuncs[C._ENUM_PAIR_SPEC] = enumPairSpecPrefixedLen
cPutFuncs[C._ENUM_PAIR_SPEC] = enumPairSpecPutter
cGetFuncs[C._ENUM_PAIR_SPEC] = enumPairSpecGetter

# ---------------------------------------------------------


def enumSpecLen(val, n):
    # val is guaranteed to be a well-formed EnumSpec object

    count = lStringLen(val.name, 0)               # field 0 contribution
    for pair in val:
        count += enumPairSpecPrefixedLen(pair, 1)   # field 1 contribution(s)
    return count


def enumSpecPrefixedLen(val, n):
    # val is guaranteed to be a well-formed EnumSpec object

    # we are going to write the header, then a byte count, then the enum
    # name, then one or more EnumPairSpecs
    h = lengthAsVarint(fieldHdrLen(n, LEN_PLUS_TYPE))
    count = enumSpecLen(val, n)
    return h + lengthAsVarint(count) + count


def enumSpecPutter(chan, val, n):
    # write the field header
    writeRawVarint(chan, fieldHdr(n, LEN_PLUS_TYPE))
#   print "AFTER WRITING HEADER pos = %u" %  pos

    # write the byte count
    count = enumSpecLen(val, n)
    writeRawVarint(chan, count)
#   print "AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write the enum's name
    lStringPut(chan, val.name, 0)             # field 0

    # write the pairs
    for pair in val:
        enumPairSpecPutter(chan, pair, 1)   # field 1 instances


def enumSpecGetter(chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = readRawVarint(chan)
    end = chan.position + byteCount           # XXX should use for validation

    # read field 0
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    s = readRawLenPlus(chan)
    name = s.decode('utf-8')                  # convert bytes to str

    # read instances of field 1: should enforce the + quantifier here
    pairs = []
    while chan.position < end:
        hdr = readRawVarint(chan)
        if hdrFieldNbr(hdr) != 1:
            # XXX SHOULD COMPLAIN IF WRONG HEADER
            # XXX This is a a peek: pos only gets advanced if OK
            print("EXPECTED FIELD 1, FOUND %s" % hdrFieldNbr(hdr))
            break
        e = enumPairSpecGetter(chan0)
        pairs.append(e)

    # create EnumSpec instance, which gets returned
    val = EnumSpec(name, pairs)
    return val

cLenFuncs[C._ENUM_SPEC] = enumSpecLen
cPLenFuncs[C._ENUM_SPEC] = enumSpecPrefixedLen
cPutFuncs[C._ENUM_SPEC] = enumSpecPutter
cGetFuncs[C._ENUM_SPEC] = enumSpecGetter

# ---------------------------------------------------------


def fieldSpecLen(val, n):
    # val is guaranteed to be a well-formed fieldSpec object
    # fields are '_name', '_type', '_quantifier', '_fieldNbr', '_default'

    count = lStringLen(val.name, 0)      # field 0 contribution
    count += vEnumLen(val.fTypeNdx, 1)
    count += vEnumLen(val.quantifier, 2)
    count += vuInt32Len(val.fieldNbr, 3)
    if val.default is not None:
        # TYPE OF DEFAULT VALUE MUST MATCH val.fType
        pass
    return count


def fieldSpecPrefixedLen(val, n):
    # val is guaranteed to be a well-formed fieldSpec object
    h = lengthAsVarint(fieldHdrLen(n, LEN_PLUS_TYPE))
    count = fieldSpecLen(val, n)
    return h + lengthAsVarint(count) + count


def fieldSpecPutter(chan, val, n):
    # fields are '_name', '_type', '_quantifier', '_fieldNbr', '_default'

    # write the field header
    writeRawVarint(chan, fieldHdr(n, LEN_PLUS_TYPE))
#   print "FIELD SPEC: AFTER WRITING HEADER pos = %u" %  pos

    # write the byte count
    count = fieldSpecLen(val, n)
    writeRawVarint(chan, count)
#   print "FIELD SPEC: AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write the field's name
    lStringPut(chan, val.name, 0)             # field 0

    # write the type
    vEnumPut(chan, val.fTypeNdx, 1)

    # write the quantifier
    vEnumPut(chan, val.quantifier, 2)

    # write the field number
    vuInt32Put(chan, val.fieldNbr, 3)

    # write the default, should there be one
    if val.default is not None:
        # XXX STUB XXX
        pass


def fieldSpecGetter(msgReg, chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = readRawVarint(chan)
    end = chan.position + byteCount

    # read field 0
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    s = readRawLenPlus(chan)
    name = s.decode('utf-8')                      # convert bytes to str

    # read field 1
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    fType = vEnumGet(chan)

    # read field 2
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    quant = vEnumGet(chan)

    # read field 3
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    fNbr = vEnumGet(chan)

    # XXX IGNORING DEFAULT
    default = None
    val = FieldSpec(msgReg, name, fType, quant, fNbr, default)

    return val

cLenFuncs[C._FIELD_SPEC] = fieldSpecLen
cPLenFuncs[C._FIELD_SPEC] = fieldSpecPrefixedLen
cPutFuncs[C._FIELD_SPEC] = fieldSpecPutter
cGetFuncs[C._FIELD_SPEC] = fieldSpecGetter

# ---------------------------------------------------------
# XXX use of 'n' parameter ?


def msgSpecLen(val, n):
    # val is guaranteed to be a well-formed msgSpec object
    # fields are  protocol, name, fields, enum=None

    count = lStringLen(val.name, 0)                # field 0, name
    for field in val:
        count += fieldSpecPrefixedLen(field, 1)     # field 1, fields
    if val.enums is not None and val.enums != []:
        for enum in val.enums:
            count += enumSpecPrefixedLen(enum, 2)   # field 2, optional enums
    return count


def msgSpecPrefixedLen(val, n):
    # val is guaranteed to be a well-formed msgSpec object
    h = lengthAsVarint(fieldHdrLen(n, LEN_PLUS_TYPE))
    count = msgSpecLen(val, n)
    return h + lengthAsVarint(count) + count


def msgSpecPutter(chan, val, n):
    # fields are  protocol, name, fields, enum=None

    # write the field header
    writeRawVarint(chan, fieldHdr(n, LEN_PLUS_TYPE))
    print("MSG SPEC: AFTER WRITING HEADER pos = %u" % chan.position)

    # write the byte count
    count = msgSpecLen(val, n)
    writeRawVarint(chan, count)
    print("MSG SPEC: AFTER WRITING BYTE COUNT %u pos = %u" % (
        count, chan.position))

    # write the spec's name
    lStringPut(chan, val.name, 0)                 # field 0

    # write the fields
    for field in val:
        fieldSpecPutter(chan, field, 1)          # field 1 instances

    # write the enum, should there be one
    if val.enums is not None and val.enums != []:
        for enum in val.enums:
            enumSpecPutter(chan, enum, 2)         # yup, field 2


def msgSpecGetter(chan):
    # read the byte count, the length of the spec
    byteCount = readRawVarint(chan)
    end = chan.position + byteCount

    # read field 0
    hdr = readRawVarint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    s = readRawLenPlus(chan)
    name = s.decode('utf8')                 # convert byte to str

    # read instances of field 1: should enforce the + quantifier here
    fields = []
    while chan.position < end:
        hdr = readRawVarint(chan)
        if hdrFieldNbr(hdr) != 1:
            # XXX SHOULD COMPLAIN IF WRONG HEADER
            # XXX This is a a peek: pos only gets advanced if OK
            print("EXPECTED FIELD 1, FOUND %s" % hdrFieldNbr(hdr))
            break
        f = fieldSpecGetter(chan0)
        fields.append(f)

    # we may have multiple enums
    enums = []
    while chan.position < end:
        hdr = readRawVarint(chan)
        if hdrFieldNbr(hdr) != 2:
            print("EXPECTED FIELD 2, FOUND %s" % hdrFieldNbr(hdr))
            break
        enum = enumSpecGetter(chan0)
        enums.append(enum)

    val = MsgSpec(name, fields, enums)

    return val

cLenFuncs[C._MSG_SPEC] = msgSpecLen
cPLenFuncs[C._MSG_SPEC] = msgSpecPrefixedLen
cPutFuncs[C._MSG_SPEC] = msgSpecPutter
cGetFuncs[C._MSG_SPEC] = msgSpecGetter

# ---------------------------------------------------------


def seqSpecLen(val, n):
    # val is guaranteed to be a well-formed seqSpec object
    pass


def seqSpecPrefixedLen(val, n):
    # val is guaranteed to be a well-formed seqSpec object
    pass


def seqSpecPutter(chan, val, n):
    # STUB
    pass


def seqSpecGetter(chan):
    # STUB
    return val

cLenFuncs[C._SEQ_SPEC] = seqSpecLen
cPLenFuncs[C._SEQ_SPEC] = seqSpecPrefixedLen
cPutFuncs[C._SEQ_SPEC] = seqSpecPutter
cGetFuncs[C._SEQ_SPEC] = seqSpecGetter

# ---------------------------------------------------------


def protoSpecLen(val, n):
    # val is guaranteed to be a well-formed protoSpec object
    pass


def protoSpecPrefixedLen(val, n):
    # val is guaranteed to be a well-formed protoSpec object
    pass


def protoSpecPutter(chan, val, n):
    # STUB
    pass


def protoSpecGetter(chan):
    # STUB
    return val              # END DISPATCH TABLES

cLenFuncs[C._PROTO_SPEC] = protoSpecLen
cPLenFuncs[C._PROTO_SPEC] = protoSpecPrefixedLen
cPutFuncs[C._PROTO_SPEC] = protoSpecPutter
cGetFuncs[C._PROTO_SPEC] = protoSpecGetter
