# fieldz/tfbuffer.py

import ctypes
import sys

import wireops.chan
from wireops.raw import(
    # VARINT_TYPE,                            # PACKED_VARINT_TYPE,
    B32_TYPE, B64_TYPE, LEN_PLUS_TYPE,
    B128_TYPE, B160_TYPE, B256_TYPE,

    # field_hdr, field_hdr_len,
    read_field_hdr,
    # hdr_field_nbr, hdr_type,
    # length_as_varint, write_varint_field,
    read_raw_varint, write_raw_varint,
    read_raw_b32,           # write_b32_field,
    read_raw_b64,           # write_b64_field,
    read_raw_len_plus,      # write_len_plus_field,
    read_raw_b128,          # write_b128_field,
    read_raw_b160,          # write_b160_field,
    read_raw_b256,          # write_b256_field,
    # next_power_of_two,
    # WireBuffer,
)

from wireops.typed import T_PUT_FUNCS, T_GET_FUNCS  # , T_LEN_FUNCS
from wireops.field_types import FieldTypes as ftypes, FieldStr as fstr

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
        #super(TFReader, self).__init__(msgSpec, len(buffer), buffer)
        super(TFReader, self).__init__(msg_spec, nnn, buffer)
        # this is a decision: we could read the first field
        self._field_nbr = -1
        self._field_type = -1
        self._p_type = -1
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
        field_type = self._field_type = self._msg_spec.field_type_ndx(
            self._field_nbr)

        # gets through dispatch table -------------------------------
        if field_type >= 0 and field_type <= ftypes.V_SINT64:
            self._value = T_GET_FUNCS[field_type](self)
            return

        # we use the field type to verify that have have read the right
        # primitive type
#       # - implemented using varints -------------------------------
#       if self._fType <= ftypes._V_UINT64:
#           if self._pType != VARINT_TYPE:
#               raise RuntimeError("pType is %u but should be %u" % (
#                                       self._pType, VARINT_TYPE))
#           (self._value, self._position) = readRawVarint(
#                                           self)
#           # DEBUG
#           print "getNext: readRawVarint returns value = 0x%x" % self._value
#           # END
#           if self._fType == ftypes._V_SINT32:
#               self._value = decodeSint32(self._value)
#               # DEBUG
#               print "    after decode self._value is 0x%x" % self._value
#               #
#           elif self._fType == ftypes._V_SINT64:
#               self._value = decodeSint64(self._value)

#           #END VARINT_GET

        # implemented using B32 -------------------------------------
        if self._field_type <= ftypes.F_FLOAT:
            self._p_type = B32_TYPE              # DEBUG
            varint_ = read_raw_b32(self)
            if self._field_type == ftypes.F_UINT32:
                self._value = ctypes.c_uint32(varint_).value
            elif self._field_type == ftypes.F_SINT32:
                self._value = ctypes.c_int32(varint_).value
            else:
                raise NotImplementedError('B32 handling for float')

        # implemented using B64 -------------------------------------
        elif self._field_type <= ftypes.F_DOUBLE:
            self._p_type = B64_TYPE              # DEBUG
            (varint_, self._position) = read_raw_b64(self)
            if self._field_type == ftypes.F_UINT64:
                self._value = ctypes.c_uint64(varint_).value
            elif self._field_type == ftypes.F_SINT64:
                self._value = ctypes.c_int64(varint_).value
            else:
                raise NotImplementedError('B64 handling for double')

        # implemented using LEN_PLUS --------------------------------
        elif self._field_type <= ftypes.L_MSG:
            self._p_type = LEN_PLUS_TYPE         # DEBUG
            varint_ = read_raw_len_plus(self)
            if self._field_type == ftypes.L_STRING:
                self._value = varint_.decode('utf-8')
            elif self._field_type == ftypes.L_BYTES:
                self._value = varint_
            else:
                raise NotImplementedError('LEN_PLUS handled as L_MSG')

        # implemented using B128, B160, B256 ------------------------
        elif self._field_type == ftypes.F_BYTES16:
            self._p_type = B128_TYPE             # DEBUG
            self._value = read_raw_b128(self)
        elif self._field_type == ftypes.F_BYTES20:
            self._p_type = B160_TYPE             # DEBUG
            self._value = read_raw_b160(self)
        elif self._field_type == ftypes.F_BYTES32:
            self._p_type = B256_TYPE             # DEBUG
            self._value = read_raw_b256(self)

        else:
            raise NotImplementedError(
                "decode for type %d has not been implemented" % self._field_type)

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

        # getter has range check
        field_type = self._msg_spec.field_type_ndx(field_nbr)

        # puts through dispatch table -------------------------------
        if 0 <= field_type and field_type <= ftypes.F_BYTES32:
            # DEBUG
            print(
                "putNext: field type is %d (%s)" %
                (field_type, fstr.as_str(field_type)))
            sys.stdout.flush()
            # END
            T_PUT_FUNCS[field_type](self, value, field_nbr)
            # DEBUG
            if field_type < ftypes.L_STRING:
                print("putNext through dispatch table:\n"
                      "         field   %u\n"
                      "         fType   %u,  %s\n"
                      "         value   %d (0x%x)\n"
                      "         offset  %u" % (
                          field_nbr, field_type, fstr.as_str(field_type),
                          value, value, self._position))
            # END
            return
        else:
            print("unknown/unimplemented field type %s" % str(field_type))

        # -- NOW VESTIGIAL ------------------------------------------
        varint_ = None
