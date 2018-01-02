# fieldz/tfbuffer.py

import ctypes
import sys

import wireops.chan
from wireops.enum import FieldTypes, PrimTypes

from wireops.raw import(
    read_field_hdr,
    # read_raw_varint, write_raw_varint,
    read_raw_b32,           # write_b32_field,
    read_raw_b64,           # write_b64_field,
    read_raw_len_plus,      # write_len_plus_field,
    read_raw_b128,          # write_b128_field,
    read_raw_b160,          # write_b160_field,
    read_raw_b256,          # write_b256_field,
)

from wireops.typed import T_PUT_FUNCS, T_GET_FUNCS  # , T_LEN_FUNCS

from fieldz import FieldzError
from fieldz.msg_spec import MsgSpec

__all__ = [\
    # value uncertain
    'TFBuffer', 'TFReader', 'TFWriter',
]

# -- CLASSES --------------------------------------------------------


class TFBuffer(wireops.chan.Channel):

    def __init__(self, msg_spec, nnn=1024, buffer=None):
        super(TFBuffer, self).__init__(nnn, buffer)
        if msg_spec is None:
            raise FieldzError('no msgSpec')
        if not isinstance(msg_spec, MsgSpec):
            raise FieldzError('object is not a MsgSpec')
        self._msg_spec = msg_spec

    @classmethod
    def create(cls, msg_spec, nnn):
        if nnn <= 0:
            raise FieldzError("buffer size must be a positive number")
        buffer = bytearray(nnn)
        return cls(msg_spec, nnn, buffer)


class TFReader(TFBuffer):
    # needs some thought; the pType is for debug
    # __slots__ = ['_field_nbr', '_field_type', '_p_type', '_value', ]

    def __init__(self, msg_spec, nnn, buffer):
        # super(TFReader, self).__init__(msgSpec, len(buffer), buffer)
        super(TFReader, self).__init__(msg_spec, nnn, buffer)
        # this is a decision: we could read the first field
        self._field_nbr = -1
        self._field_type = None
        self._p_type = None
        self._value = None

    # def create(n) inherited

    @property
    def field_nbr(self):
        return self._field_nbr

    @property
    def field_type(self):
        return self._field_type

    @property
    def p_type(self):
        return self._p_type      # for DEBUG

    @property
    def value(self):
        return self._value

    def get_next(self):
        (self._p_type, self._field_nbr) = read_field_hdr(self)

        # getter has range check
        # pylint: disable=not-callable
        field_type = self._field_type = FieldTypes(
            self._msg_spec.field_type_from_nbr(self._field_nbr))

        # DEBUG
        print("TFReader.get_next: field_type is %s (%d)" % (
            field_type.sym, field_type.value))
        # END

        # gets through dispatch table -------------------------------
        # XXX IMPROPER USE OF KNOWLEDGE OF ORDER OF MEMBERS
        # pylint: disable=no-member
        if field_type.value >= 0 and field_type.value <= FieldTypes.V_SINT64:
            self._value = T_GET_FUNCS[field_type](self)
            return

        # we use the field type to verify that have have read the right
        # primitive type
#       # - implemented using varints -------------------------------
#       if self._fType <= FieldTypes._V_UINT64:
#           if self._pType != VARINT_TYPE:
#               raise RuntimeError("pType is %u but should be %u" % (
#                                       self._pType, VARINT_TYPE))
#           (self._value, self._position) = readRawVarint(
#                                           self)
#           # DEBUG
#           print "getNext: readRawVarint returns value = 0x%x" % self._value
#           # END
#           if self._fType == FieldTypes._V_SINT32:
#               self._value = decodeSint32(self._value)
#               # DEBUG
#               print "    after decode self._value is 0x%x" % self._value
#               #
#           elif self._fType == FieldTypes._V_SINT64:
#               self._value = decodeSint64(self._value)

#           #END VARINT_GET

        # implemented using B32 -------------------------------------
        if self._field_type <= FieldTypes.F_FLOAT:
            self._p_type = PrimTypes.B32              # DEBUG
            varint_ = read_raw_b32(self)
            if self._field_type == FieldTypes.F_UINT32:
                self._value = ctypes.c_uint32(varint_).value
            elif self._field_type == FieldTypes.F_SINT32:
                self._value = ctypes.c_int32(varint_).value
            else:
                raise NotImplementedError('B32 handling for float')

        # implemented using B64 -------------------------------------
        elif self._field_type <= FieldTypes.F_DOUBLE:
            self._p_type = PrimTypes.B64              # DEBUG
            (varint_, self._position) = read_raw_b64(self)
            if self._field_type == FieldTypes.F_UINT64:
                self._value = ctypes.c_uint64(varint_).value
            elif self._field_type == FieldTypes.F_SINT64:
                self._value = ctypes.c_int64(varint_).value
            else:
                raise NotImplementedError('B64 handling for double')

        # implemented using LEN_PLUS --------------------------------
        elif self._field_type <= FieldTypes.L_MSG:
            self._p_type = PrimTypes.LEN_PLUS         # DEBUG
            varint_ = read_raw_len_plus(self)
            # pylint: disable=no-member
            if self._field_type == FieldTypes.L_STRING:
                self._value = varint_.decode('utf-8')
            elif self._field_type == FieldTypes.L_BYTES:
                self._value = varint_
            else:
                raise NotImplementedError('LEN_PLUS handled as L_MSG')

        # implemented using B128, B160, B256 ------------------------
        elif self._field_type == FieldTypes.F_BYTES16:
            self._p_type = PrimTypes.B128             # DEBUG
            self._value = read_raw_b128(self)
        elif self._field_type == FieldTypes.F_BYTES20:
            self._p_type = PrimTypes.B160             # DEBUG
            self._value = read_raw_b160(self)
        elif self._field_type == FieldTypes.F_BYTES32:
            self._p_type = PrimTypes.B256             # DEBUG
            self._value = read_raw_b256(self)

        else:
            raise NotImplementedError(
                "decode for type %d has not been implemented" %
                self._field_type)

        # END GET


class TFWriter(TFBuffer):
    # needs some thought; MOSTLY FOR DEBUG

    __slots__ = ['_field_nbr', '_field_type', '_p_type', '_value', ]

    def __init__(self, msg_spec, nnn=1024, buffer=None):
        super(TFWriter, self).__init__(msg_spec, nnn, buffer)
        # this is a decision: we could read the first field
        self._field_nbr = -1
        self._field_type = -1
        self._p_type = -1
        self._value = None

    # def create(n) inherited

    # These are for DEBUG
    @property
    def field_nbr(self):
        return self._field_nbr

    @property
    def field_type(self):
        return self._field_type

    @property
    def p_type(self):
        return self._p_type

    @property
    def value(self):
        return self._value
    # END DEBUG PROPERTIES

    def put_next(self, field_nbr, value):
        # DEBUG
        print("TFWriter.put_next: field_nbr %d" % field_nbr)
        # END
        # getter has range check
        field_type = self._msg_spec.field_type_from_nbr(field_nbr)  # LINE 210

        # puts through dispatch table -------------------------------
        # XXX REMOVED RANGE CHECK
        # DEBUG
        print(
            "putNext: field type is %s (%d)" %
            (field_type.sym, field_type.value))

        if isinstance(value, int):
            print("    value is %d" % value)
        else:
            print("    value is %s" % value)
        print("    position is %u" % self._position)
        sys.stdout.flush()
        # END
        T_PUT_FUNCS[field_type](self, value, field_nbr)

        return

        # THIS CODE IS UNREACHABLE, so commented it out
#         # DEBUG ### IMPROPER USE OF KNOWLEDGE OF ORDER OF FIELD NUMBERS
#         # pylint: disable=no-member
#         if field_type.value < FieldTypes.L_STRING.value:
#             msg = "putNext through dispatch table:\n" +\
#                   "field   %u\n" % field_nbr +\
#                   "fType   %u,  %s\n" % (field_type.sym, field_type.value) +\
#                   "value   %d (0x%x)\n" % (value, value) +\
#                   "offset  %u" % self._position
# #               field_nbr, field_type.sym, field_type.value,
# #               value, value,
# #               self._position)
#             print(msg)
#         # END
#         return
