# fieldz/msgSpec.py

import re
import sys

#from fieldz.raw import *
#from fieldz.typed import *

from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.core_types as C

__all__ = [\
    # constants, so to speak: quantifiers
    'Q_REQUIRED',   # no quantifier, so one and only one such field
    'Q_OPTIONAL',   # ?: either zero or one instance of the field
    'Q_STAR',       # *: zero or more instances of the field allowed
    'Q_PLUS',       # +: one or more instances of the field
    'Q_NAMES',      # list of the four above
    # methods
    'q_name', 'validate_dimple_name', 'validate_dotted_name',

    # class-level
    'C_PUT_FUNCS', 'C_GET_FUNCS', 'C_LEN_FUNCS',

    'enum_pair_spec_putter', 'enum_spec_putter', 'field_spec_putter',
    'msg_spec_putter', 'seq_spec_putter', 'proto_spec_putter',

    'enum_pair_spec_getter', 'enum_spec_getter', 'field_spec_getter',
    'msg_spec_getter', 'seq_spec_getter', 'proto_spec_getter',

    'enum_pair_spec_len', 'enum_spec_len', 'field_spec_len',
    'msg_spec_len', 'seq_spec_len', 'proto_spec_len',

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


def q_name(nnn):
    if nnn < 0 or nnn >= len(Q_NAMES):
        raise ValueError('does not map to a valid quantifier: %s' % str(nnn))
    return Q_NAMES[nnn]

# base names, forming part of a larger pattern
_VALID_NAME_PAT = "[a-zA-Z_][a-zA-Z_0-9]*"
_VALID_NAME_RE = re.compile(_VALID_NAME_PAT)

# just base names; match will fail if any further characters follow
_VALID_SIMPLE_NAME_PAT = _VALID_NAME_PAT + '$'
_VALID_SIMPLE_NAME_RE = re.compile(_VALID_SIMPLE_NAME_PAT)


def validate_dimple_name(string):
    match = _VALID_SIMPLE_NAME_RE.match(string)
    if match is None:
        raise RuntimeError("invalid simple name '%s'" % string)

# both protocol names and field names can be qualified
_VALID_DOTTED_NAME_PAT = _VALID_NAME_PAT + '(\.' + _VALID_NAME_PAT + ')*$'
_VALID_DOTTED_NAME_RE = re.compile(_VALID_DOTTED_NAME_PAT)


def validate_dotted_name(string):
    match = _VALID_DOTTED_NAME_RE.match(string)
    if match is None:
        raise RuntimeError("invalid (optionally dotted) name %s'" % string)


# -- CLASSES --------------------------------------------------------
class EnumPairSpec(object):
    __slots__ = ['_symbol', '_value', ]

    def __init__(self, symbol, value):
        validate_dimple_name(symbol)
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

    def indented_str(self, indent='', step=''):
        return "%s%s = %d\n" % (indent, self._symbol, self._value)

    def __str__(self):
        """ return a usable representation of the EnumPairSpec """
        return self.indented_str('    ')

    def __repr__(self):
        """ return the EnumPairSpec in today's notion of the canonical form """
        return self.indented_str(' ')


class EnumSpec(object):
    """
    For our purposes an enum is a named list of simple names (names
    containing no delimiters)` and a map from such names to their
    non-negative integer values.
    """
    __slots__ = ['_name', '_pairs', '_sym2pair', ]

    def __init__(self, name, pairs):
        """pairs are EnumPairSpecs """
        validate_dotted_name(name)
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
        validate_dotted_name(name)
        if pairs is None:
            raise ValueError('null list of enum pairs')
        if len(pairs) == 0:
            raise ValueError('empty list of enum pairs')

        _pairs = []
        for pair in pairs:
            sym = pair[0]
            val = pair[1]
            ppp = EnumPairSpec(sym, val)
            _pairs.append(ppp)
        return EnumSpec(name, _pairs)

    def value(self, string):
        """ map a name to the corresponding value """
        return self._sym2pair[string].value

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
            if self[i].symbol != other[i].symbol or\
                    self[i].value != other[i].value:
                print("ENUM_PAIR_SPECS DIFFER:")
                print("  my    pair %u: %s" % (i, self[i]))
                print("  other pair %u: %s" % (i, other[i]))
                return False
        return True

    def indented_str(self, indent='', step=''):
        # DEBUG
        print("EnumSpec.indentedStr <-------------------")
        # END
        string = []
        string.append('%senum %s\n' % (indent, self.name))
        for pair in self._pairs:
            string.append(pair.indented_str(indent + step, step))
        return ''.join(string)

    def __str__(self):
        """ return a usable representation of the EnumSpec """
        return self.indented_str('', '    ')

    def __repr__(self):
        """ return the EnumSpec in today's notion of the canonical form """
        return self.indented_str('', ' ')


class FieldSpec(object):
    __slots__ = ['_reg',
                 '_name', '_type', '_quantifier', '_field_nbr', '_default', ]

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
        if self._field_nbr:
            if other._field_nbr is None:
                print("OTHER FIELD_SPEC HAS NO FIELD NBR")
                return False
            if self._field_nbr != other._field_nbr:
                print("FIELD_SPEC FIELD NBRS DIFFER")
                return False

        # XXX IGNORE DEFAULTS FOR NOW

        return True

    def __init__(self, reg, name, field_type, quantifier=Q_REQUIRED,
                 field_nbr=-1, default=None):
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
        validate_dotted_name(name)
        self._name = name

        # -- fType --------------------------------------------------
        if field_type < 0 or field_type > F.MAX_NDX:
            raise ValueError("invalid fType '%s'" % str(field_type))
        self._type = field_type

        # -- quantifier ---------------------------------------------
        # XXX BAD RANGE CHECK ??
        if quantifier < 0 or quantifier > Q_PLUS:
            raise ValueError("invalid quantifier '%s'" % str(quantifier))
        self._quantifier = quantifier

        # -- fieldNbr -----------------------------------------------
        self._field_nbr = int(field_nbr)

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
    def field_type_name(self):
        if 0 <= self._type and self._type <= F.MAX_NDX:
            return FS().as_str(self._type)
        reg_id = self._reg.reg_id2name(self._type)
        if reg_id is None:
            # XXX parent must search upwards if not found
            reg_id = self._reg.parent.reg_id2name(self._type)
        return reg_id

    # XXX return a number
    @property
    def FIELD_TYPE_NDX(self): return self._type

    @property
    def quantifier(self): return self._quantifier
    #def quantifier(self):   return Q_NAMES[self._quantifier]

    @property
    def field_nbr(self):
        return self._field_nbr

    @field_nbr.setter
    def field_nbr(self, value):
        varint_ = int(value)
        if varint_ < 0:
            raise ValueError('field number may not be negative')
        self._field_nbr = varint_

    @property
    def default(self): return self._default

    def indented_str(self, indent, step):
        string = []
        string.append('%s%s ' % (indent, self._name))

        tName = self.field_type_name
        if self._quantifier != Q_REQUIRED:
            tName += q_name(self._quantifier)
        string.append('%s ' % tName)               # at least one space

        if self._field_nbr is not None:
            # again, at least one space
            string.append('@%d ' % self._field_nbr)

        #========================
        # XXX default not handled
        #========================
        string.append('\n')

        return '' . join(string)

    def __str__(self):
        """ return a prettier representation of the FieldSpec """
        return self.indented_str('', '    ')

    def __repr__(self):
        """
        Return the FieldSpec in today's notion of the canonical form.
        This doesn't have to be pretty, just absolutely clear and
        unambiguous.
        """
        return self.indented_str('', ' ')


class SeqSpec(object):
    """

    """

    def __init__(self):
        pass
        # XXX STUB

    def indented_str(self, indent, step):
        raise NotImplementedError('indentedStr for SeqSpec')

    def __str__(self):
        return self.indented_str('', '    ')

    def __repr__(self):
        return self.indented_str('', ' ')                # GEEP

# SUPER SPECS =======================================================


class SuperSpec(object):
    __slots__ = ['_name', '_parent', '_my_reg', '_enums', '_msgs',
                 '_msgs_by_name', '_msg_name_ndx', '_nextMsg',
                 ]

    def __init__(self, name, reg, parent=None):
        if name is None:
            raise ValueError('missing protocol name')
        validate_dotted_name(name)
        self._name = name

        if reg is None:
            raise ValueError('proto reg must be specified')
        self._my_reg = reg

        self._parent = parent

        self._enums = []
        self._msgs = []
        self._msgs_by_name = {}
        self._msg_name_ndx = {}    # map name to index
        self._nextMsg = 0

    @property
    def name(self): return self._name

    @property
    def parent(self): return self._parent             # FOO

    @property
    def reg(self): return self._my_reg          # this protocol's reg

    # XXX we should make iterators available instead
    @property
    def enums(self): return self._enums

    @property
    def msgs(self): return self._msgs

    def add_enum(self, exc):
        # should validate AND check for uniqueness

        # DEBUG
        name = exc.name
        print("ADDING ENUM %s TO SUPER_SPEC" % name)
        # END

        # WORKING HERE
        self._enums.append(exc)

    def add_msg(self, match):
        name = match.name
        # XXX This forbids shadowing of the name in the parent but
        #     not further up the tree
        if name in self._msgs_by_name or (self.parent is not None
                                          and name in self.parent._msgs_by_name):
            raise RuntimeError("name '%s' is already in use" % name)
        print("ADDING MSG %d '%s' TO PROTO SPEC LIST" %
              (self._nextMsg, name))         # DEBUG
        self._msgs.append(match)
        self._msgs_by_name[name] = match                             # FOO
        self._msg_name_ndx[name] = self._nextMsg
        self._nextMsg += 1

    def get_msg_spec(self, name):
        """ given a name, returns the corresponding msgSpec """
        return self._msgs_by_name[name]

    def msg_name_index(self, name):
        """ given a name, returns its index """
        return self._msg_name_ndx[name]

    # XXX USELESS IN ITS PRESENT STATE ------------------------------
    def get_reg_id_for_name(self, name):
        """
        If the name is in use, raise an exception.  Otherwise, return
        the next free regID.
        """

        # THIS LOGIC DOESN'T PERMIT FULLY RECURSIVE STRUCTURE

        # XXX THIS IS NONSENSE: there is no MsgSpec._byName

        if name in self._msgs_by_name or name in self.parent._msgs_by_name:
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

    def addSeq(self, string):
        # should validate AND check for uniqueness
        self._seqs.append(string)

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
            nnn = len(self._enums)
            if nnn != len(other._enums):
                return False
            for i in range(nnn):
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
            nnn = len(self._msgs)
            if nnn != len(other._msgs):
                return False
            for i in range(nnn):
                if not self._msgs[i].__eq__(other._msgs[i]):
                    return False

        if self._seqs is None:
            if other._seqs is not None:
                return False
        else:
            if other._seqs is None:
                return False
            nnn = len(self._seqs)
            if nnn != len(other._seqs):
                return False
            for i in range(nnn):
                if self._seqs[i] != other._seqs[i]:
                    return False

        return True

    def indented_str(self, indent='', step=' '):
        string = []
        string.append("%sprotocol %s\n" % (indent, self._name))
        if self._enums is not None:
            for exc in self._enums:
                string.append(exc.indented_str(indent, step))
        if self._msgs is not None:
            for match in self._msgs:
                print("DEBUG: ProtoSpec SERIALIZING " + match.name)
                string.append(match.indented_str(indent, step))
        if self._seqs is not None:
            for qqq in self._seqs:
                string.append(qqq.indented_str(indent, step))

        return ''.join(string)

    def __str__(self):
        return self.indented_str('', '    ')

    def __repr__(self):
        return self.indented_str('', ' ')                        # GEEP


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

    # XXX 2016-06-24 inverted order of last two paramaters
    def __init__(self, name, reg, parent):
        # if parent is None:
        #    raise ValueError('parent must be specified')
        name = str(name)
        validate_dimple_name(name)
        super(MsgSpec, self).__init__(name, reg, parent)

        # XXX QUESTIONABLE
        if parent:
            parent.add_msg(self)

        self._fields = []
        self._lastFieldNbr = -1
        self.fieldNameToNdx = {}    # XXX value?
        self._fieldNdx = 0     # zero-based index of field in MsgSpec

    def addField(self, file):
        f_name = file.name
        if not isinstance(file, FieldSpec):
            raise ValueError("'%s' is not a FieldSpec!" % f_name)
        if f_name in self.fieldNameToNdx:
            raise KeyError("field named %s already exists" % f_name)
        if file.field_nbr < 0:
            self._lastFieldNbr += 1
            file.field_nbr = self._lastFieldNbr
        elif file.field_nbr <= self._lastFieldNbr:
            raise ValueError(
                "field number is %d not greater than last %d" % (
                    file.field_nbr, self._lastFieldNbr))
        else:
            self._lastFieldNbr = file.field_nbr
        self._fields.append(file)
        self.fieldNameToNdx[f_name] = self._fieldNdx
        self._fieldNdx += 1         # so this is a count of fields

    def __len__(self): return len(self._fields)

    def __getitem__(self, k):
        """ iterates over fields of the message """
        return self._fields[k]

    def f_name(self, i):
        if self.__len__() == 0:
            raise ValueError("INTERNAL ERROR: message has no fields")
        if i < 0 or i >= self.__len__():
            raise ValueError('field number %d out of range' % i)
        return self._fields[i].name

    def field_type_name(self, i):
        # field numbers are zero-based
        if self.__len__() == 0:
            raise ValueError("INTERNAL ERROR: message has no fields")
        if i < 0 or i >= self.__len__():
            raise ValueError('field number %d out of range' % i)
        # XXX WRONG-ish: fType MUST be numeric; this should return
        # the string equivalent; HOWEVER, if the type is lMsg, we
        # want to return the message name ... XXX
        return self._fields[i].field_type_name

    def FIELD_TYPE_NDX(self, i):
        # field numbers are zero-based
        if self.__len__() == 0:
            raise ValueError("INTERNAL ERROR: message has no fields")
        if i < 0 or i >= self.__len__():
            raise ValueError('field number %d out of range' % i)

        # XXX WRONG-ish: fType MUST be numeric; this should return
        # the string equivalent; HOWEVER, if the type is lMsg, we
        # want to return the message name ... XXX
        return self._fields[i].FIELD_TYPE_NDX

    def field_default(self, i):
        # field numbers are zero-based
        if self.__len__() == 0:
            raise ValueError("INTERNAL ERROR: message has no fields")
        if i < 0 or i >= self.__len__():
            raise ValueError('field number %d out of range' % i)
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
        for nnn in range(self.__len__()):
            if not self._fields[nnn].__eq__(other._fields[nnn]):
                return False
        return True

    def indented_str(self, indent, step):
        string = []
        # s.append( "%sprotocol %s\n\n" % (indent, self._protocol))
        string.append("%smessage %s\n" % (indent, self._name))
        if self._enums is not None:
            for exc in self._enums:
                string.append(exc.indented_str(indent + step, step))
        if self._msgs is not None:
            for match in self._msgs:
                -string.append(match.indented_str(indent + step, step))
        for file in self._fields:
            string.append(file.indented_str(indent + step, step))
        return ''.join(string)

    def __str__(self):
        """ return string representation in perhaps prettier format """
        return self.indented_str('', '    ')

    def __repr__(self):
        """ return string representation in canonical format """
        return self.indented_str('', ' ')                        # GEEP

# DISPATCH TABLES ===================================================

# XXX dunno why notImpl is not picked up by
#                                          from fieldz.typed import *


def not_impl(*arg): raise NotImplementedError

C_TYPES = C.CoreTypes()

C_PUT_FUNCS = [not_impl] * (C_TYPES.max_ndx + 1)
C_GET_FUNCS = [not_impl] * (C_TYPES.max_ndx + 1)
C_LEN_FUNCS = [not_impl] * (C_TYPES.max_ndx + 1)
C_P_LEN_FUNCS = [not_impl] * (C_TYPES.max_ndx + 1)

# PUTTERS, GETTERS, LEN FUNCS ---------------------------------------

l_string_len = T_LEN_FUNCS[F.L_STRING]
l_string_put = T_PUT_FUNCS[F.L_STRING]
vuint32_len = T_LEN_FUNCS[F.V_UINT32]
vuint32_put = T_PUT_FUNCS[F.V_UINT32]
venum_get = T_GET_FUNCS[F.V_ENUM]
venum_len = T_LEN_FUNCS[F.V_ENUM]
venum_put = T_PUT_FUNCS[F.V_ENUM]

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
# LEN PARAMETERS MUST BE (val, n), where n is the field number
# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX


def enum_pair_spec_len(val, nnn):
    """
    val is guaranteed to be a well-formed EnumPair object; this is
    the length of the spec on the wire, what is written before the spec.
    Returns the total of the encoded length of the symbol and that of
    its value.
    """
    return l_string_len(val.symbol, nnn) + vuint32_len(val.value, nnn)


def enum_pair_spec_prefixed_len(val, nnn):
    """
    val is guaranteed to be a well-formed EnumPair object; this is
    the length of the spec on the wire, what is written before the spec.
    So it is the total length of the header plus the length of the encoded
    byte count plus the length of the encoded enumPairSpec.
    """
    h = length_as_varint(field_hdr_len(nnn, LEN_PLUS_TYPE))
    byteCount = enum_pair_spec_len(val, nnn)
    return h + length_as_varint(byteCount) + byteCount

# val = instance of the type, n = field number


def enum_pair_spec_putter(chan, val, nnn):
    # write the field header
    write_raw_varint(chan, field_hdr(nnn, LEN_PLUS_TYPE))

    # write the byte count
    count = enum_pair_spec_len(val, nnn)
    write_raw_varint(chan, count)
#   print "AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write field 0, the symbol
    l_string_put(chan, val.symbol, 0)
#   print "AFTER WRITING SYMBOL %s pos = %u" % ( val.symbol, pos)

    # write field 1, the value
    vuint32_put(chan, val.value, 1)
#   print "AFTER WRITING VALUE %u pos = %u" % (val.value, pos)


def enum_pair_spec_getter(dummyReg, chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = read_raw_varint(chan)
    end = chan.position + byteCount           # XXX should use for validation

    # read field 0
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    string = read_raw_len_plus(chan)
    sym = string.decode('utf-8')                   # convert bytes to str

    # read field 1
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    val = read_raw_varint(chan)

    # construct the EnumPairSpec object from field values
    obj = EnumPairSpec(sym, val)
    return obj

C_LEN_FUNCS[C_TYPES.ENUM_PAIR_SPEC] = enum_pair_spec_len
C_P_LEN_FUNCS[C_TYPES.ENUM_PAIR_SPEC] = enum_pair_spec_prefixed_len
C_PUT_FUNCS[C_TYPES.ENUM_PAIR_SPEC] = enum_pair_spec_putter
C_GET_FUNCS[C_TYPES.ENUM_PAIR_SPEC] = enum_pair_spec_getter

# ---------------------------------------------------------


def enum_spec_len(val, nnn):
    # val is guaranteed to be a well-formed EnumSpec object

    count = l_string_len(val.name, 0)               # field 0 contribution
    for pair in val:
        # field 1 contribution(s)
        count += enum_pair_spec_prefixed_len(pair, 1)
    return count


def enumSpecPrefixedLen(val, nnn):
    # val is guaranteed to be a well-formed EnumSpec object

    # we are going to write the header, then a byte count, then the enum
    # name, then one or more EnumPairSpecs
    len_ = length_as_varint(field_hdr_len(nnn, LEN_PLUS_TYPE))
    count = enum_spec_len(val, nnn)
    return len_ + length_as_varint(count) + count


def enum_spec_putter(chan, val, nnn):
    # write the field header
    write_raw_varint(chan, field_hdr(nnn, LEN_PLUS_TYPE))
#   print "AFTER WRITING HEADER pos = %u" %  pos

    # write the byte count
    count = enum_spec_len(val, nnn)
    write_raw_varint(chan, count)
#   print "AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write the enum's name
    l_string_put(chan, val.name, 0)             # field 0

    # write the pairs
    for pair in val:
        enum_pair_spec_putter(chan, pair, 1)   # field 1 instances


def enum_spec_getter(chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = read_raw_varint(chan)
    end = chan.position + byteCount           # XXX should use for validation

    # read field 0
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    string = read_raw_len_plus(chan)
    name = string.decode('utf-8')                  # convert bytes to str

    # read instances of field 1: should enforce the + quantifier here
    pairs = []
    while chan.position < end:
        hdr = read_raw_varint(chan)
        if hdr_field_nbr(hdr) != 1:
            # XXX SHOULD COMPLAIN IF WRONG HEADER
            # XXX This is a a peek: pos only gets advanced if OK
            print("EXPECTED FIELD 1, FOUND %s" % hdr_field_nbr(hdr))
            break
        exc = enum_pair_spec_getter(chan0)
        pairs.append(exc)

    # create EnumSpec instance, which gets returned
    val = EnumSpec(name, pairs)
    return val

C_LEN_FUNCS[C_TYPES.ENUM_SPEC] = enum_spec_len
C_P_LEN_FUNCS[C_TYPES.ENUM_SPEC] = enumSpecPrefixedLen
C_PUT_FUNCS[C_TYPES.ENUM_SPEC] = enum_spec_putter
C_GET_FUNCS[C_TYPES.ENUM_SPEC] = enum_spec_getter

# ---------------------------------------------------------


def field_spec_len(val, nnn):
    # val is guaranteed to be a well-formed fieldSpec object
    # fields are '_name', '_type', '_quantifier', '_fieldNbr', '_default'

    count = l_string_len(val.name, 0)      # field 0 contribution
    count += venum_len(val.FIELD_TYPE_NDX, 1)
    count += venum_len(val.quantifier, 2)
    count += vuint32_len(val.field_nbr, 3)
    if val.default is not None:
        # TYPE OF DEFAULT VALUE MUST MATCH val.fType
        pass
    return count


def field_spec_prefixed_len(val, nnn):
    # val is guaranteed to be a well-formed fieldSpec object
    h = length_as_varint(field_hdr_len(nnn, LEN_PLUS_TYPE))
    count = field_spec_len(val, nnn)
    return h + length_as_varint(count) + count


def field_spec_putter(chan, val, nnn):
    # fields are '_name', '_type', '_quantifier', '_fieldNbr', '_default'

    # write the field header
    write_raw_varint(chan, field_hdr(nnn, LEN_PLUS_TYPE))
#   print "FIELD SPEC: AFTER WRITING HEADER pos = %u" %  pos

    # write the byte count
    count = field_spec_len(val, nnn)
    write_raw_varint(chan, count)
#   print "FIELD SPEC: AFTER WRITING BYTE COUNT %u pos = %u" % (count, pos)

    # write the field's name
    l_string_put(chan, val.name, 0)             # field 0

    # write the type
    venum_put(chan, val.FIELD_TYPE_NDX, 1)

    # write the quantifier
    venum_put(chan, val.quantifier, 2)

    # write the field number
    vuint32_put(chan, val.field_nbr, 3)

    # write the default, should there be one
    if val.default is not None:
        # XXX STUB XXX
        pass


def field_spec_getter(msg_reg, chan):
    # we have already read the header containing the field number
    # read the byte count, the length of the spec
    byteCount = read_raw_varint(chan)
    end = chan.position + byteCount

    # read field 0
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    string = read_raw_len_plus(chan)
    name = string.decode('utf-8')                      # convert bytes to str

    # read field 1
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    field_type = venum_get(chan)

    # read field 2
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    quant = venum_get(chan)

    # read field 3
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    f_nbr = venum_get(chan)

    # XXX IGNORING DEFAULT
    default = None
    val = FieldSpec(msg_reg, name, field_type, quant, f_nbr, default)

    return val

C_LEN_FUNCS[C_TYPES.FIELD_SPEC] = field_spec_len
C_P_LEN_FUNCS[C_TYPES.FIELD_SPEC] = field_spec_prefixed_len
C_PUT_FUNCS[C_TYPES.FIELD_SPEC] = field_spec_putter
C_GET_FUNCS[C_TYPES.FIELD_SPEC] = field_spec_getter

# ---------------------------------------------------------
# XXX use of 'n' parameter ?


def msg_spec_len(val, nnn):
    # val is guaranteed to be a well-formed msgSpec object
    # fields are  protocol, name, fields, enum=None

    count = l_string_len(val.name, 0)                # field 0, name
    for field in val:
        count += field_spec_prefixed_len(field, 1)     # field 1, fields
    if val.enums is not None and val.enums != []:
        for enum in val.enums:
            count += enumSpecPrefixedLen(enum, 2)   # field 2, optional enums
    return count


def msg_spec_prefixed_len(val, nnn):
    # val is guaranteed to be a well-formed msgSpec object
    h = length_as_varint(field_hdr_len(nnn, LEN_PLUS_TYPE))
    count = msg_spec_len(val, nnn)
    return h + length_as_varint(count) + count


def msg_spec_putter(chan, val, nnn):
    # fields are  protocol, name, fields, enum=None

    # write the field header
    write_raw_varint(chan, field_hdr(nnn, LEN_PLUS_TYPE))
    print("MSG SPEC: AFTER WRITING HEADER pos = %u" % chan.position)

    # write the byte count
    count = msg_spec_len(val, nnn)
    write_raw_varint(chan, count)
    print("MSG SPEC: AFTER WRITING BYTE COUNT %u pos = %u" % (
        count, chan.position))

    # write the spec's name
    l_string_put(chan, val.name, 0)                 # field 0

    # write the fields
    for field in val:
        field_spec_putter(chan, field, 1)          # field 1 instances

    # write the enum, should there be one
    if val.enums is not None and val.enums != []:
        for enum in val.enums:
            enum_spec_putter(chan, enum, 2)         # yup, field 2


# 'msgReg' param added 2016-06-24
def msg_spec_getter(msg_reg, chan):
    # read the byte count, the length of the spec
    byteCount = read_raw_varint(chan)
    end = chan.position + byteCount

    # read field 0
    hdr = read_raw_varint(chan)
    # SHOULD COMPLAIN IF WRONG HEADER
    string = read_raw_len_plus(chan)
    name = string.decode('utf8')                 # convert byte to str

    # read instances of field 1: should enforce the + quantifier here
    fields = []
    while chan.position < end:
        hdr = read_raw_varint(chan)
        if hdr_field_nbr(hdr) != 1:
            # XXX SHOULD COMPLAIN IF WRONG HEADER
            # XXX This is a a peek: pos only gets advanced if OK
            print("EXPECTED FIELD 1, FOUND %s" % hdr_field_nbr(hdr))
            break
        # XXX params should be (msgReg, chan)
        file = field_spec_getter(msg_reg, chan)       # was chan0
        fields.append(file)

    # we may have multiple enums
    enums = []
    while chan.position < end:
        hdr = read_raw_varint(chan)
        if hdr_field_nbr(hdr) != 2:
            print("EXPECTED FIELD 2, FOUND %s" % hdr_field_nbr(hdr))
            break
        enum = enum_spec_getter(chan)     # was chan0
        enums.append(enum)

    # XXX WRONG PARAMETER LIST
    # val = MsgSpec(name, fields, enums)
    dummyParent = MsgSpec('dummy', msg_reg, None)
    val = MsgSpec(name, msg_reg, dummyParent)
    return val

C_LEN_FUNCS[C_TYPES.MSG_SPEC] = msg_spec_len
C_P_LEN_FUNCS[C_TYPES.MSG_SPEC] = msg_spec_prefixed_len
C_PUT_FUNCS[C_TYPES.MSG_SPEC] = msg_spec_putter
C_GET_FUNCS[C_TYPES.MSG_SPEC] = msg_spec_getter

# ---------------------------------------------------------


def seq_spec_len(val, nnn):
    # val is guaranteed to be a well-formed seqSpec object
    pass


def seq_spec_prefixed_len(val, nnn):
    # val is guaranteed to be a well-formed seqSpec object
    pass


def seq_spec_putter(chan, val, nnn):
    # STUB
    pass


def seq_spec_getter(dummyReg, chan):
    # STUB
    return val

C_LEN_FUNCS[C_TYPES.SEQ_SPEC] = seq_spec_len
C_P_LEN_FUNCS[C_TYPES.SEQ_SPEC] = seq_spec_prefixed_len
C_PUT_FUNCS[C_TYPES.SEQ_SPEC] = seq_spec_putter
C_GET_FUNCS[C_TYPES.SEQ_SPEC] = seq_spec_getter

# ---------------------------------------------------------


def proto_spec_len(val, nnn):
    # val is guaranteed to be a well-formed protoSpec object
    pass


def proto_spec_prefixed_len(val, nnn):
    # val is guaranteed to be a well-formed protoSpec object
    pass


def proto_spec_putter(chan, val, nnn):
    # STUB
    pass


def proto_spec_getter(chan):
    # STUB
    return val              # END DISPATCH TABLES

C_LEN_FUNCS[C_TYPES.PROTO_SPEC] = proto_spec_len
C_P_LEN_FUNCS[C_TYPES.PROTO_SPEC] = proto_spec_prefixed_len
C_PUT_FUNCS[C_TYPES.PROTO_SPEC] = proto_spec_putter
C_GET_FUNCS[C_TYPES.PROTO_SPEC] = proto_spec_getter
