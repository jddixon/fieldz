# fieldz/typed.py

import ctypes
import struct
import sys

from fieldz.field_types import FieldTypes as F

from fieldz.chan import Channel
# from fieldz.raw import *

# MsgSpec cannot be imported
#from fieldz.msg_spec import  MsgSpec

__all__ = [
    'encode_sint32', 'decode_sint32',
    'encode_sint64', 'decode_sint64',
    'not_impl',
    'T_PUT_FUNCS', 'T_GET_FUNCS', 'T_LEN_FUNCS',
]


def encode_sint32(string):
    ndx_ = ctypes.c_int32(0xffffffff & string).value
    # we must have the sign filling in from the left
    varint_ = (ndx_ << 1) ^ (ndx_ >> 31)
#   # DEBUG
#   print "\nencodeSint32: 0x%x --> 0x%x" % (s, v)
#   # END
    return varint_


def decode_sint32(varint_):
    # decode zig-zag:  stackoverflow 2210923
    ndx_ = (varint_ >> 1) ^ (-(varint_ & 1))
    string = ctypes.c_int32(ndx_).value
#   # DEBUG
#   print "decodeSint32: 0x%x --> 0x%x" % (v, s)
#   # END
    return string


def encode_sint64(string):
    varint_ = ctypes.c_int64(0xffffffffffffffff & string).value
    # we must have the sign filling in from the left
    varint_ = (varint_ << 1) ^ (varint_ >> 63)
    return varint_


def decode_sint64(varint_):
    varint_ = (varint_ >> 1) ^ (-(varint_ & 1))
    string = ctypes.c_int64(varint_).value
    return string

# DISPATCH TABLES ===================================================


def not_impl(*arg):
    raise NotImplementedError

T_PUT_FUNCS = [not_impl] * (int(F.MAX_NDX) + 1)
T_GET_FUNCS = [not_impl] * (int(F.MAX_NDX) + 1)
T_LEN_FUNCS = [not_impl] * (int(F.MAX_NDX) + 1)

# puts implemented using varInts --------------------------


def vbool_put(chan, val, nnn):
    if val is True:
        write_varint_field(chan, 1, nnn)
    else:
        write_varint_field(chan, 0, nnn)
T_PUT_FUNCS[F.V_BOOL] = vbool_put


def venum_put(chan, val, nnn):
    # just handle enums as simple ints for now, but constrain
    # to 16 bits; any sign is uhm mangled
    varint_ = 0xffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[F.V_ENUM] = venum_put


def vuint32_put(chan, val, nnn):
    varint_ = 0xffffffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[F.V_UINT32] = vuint32_put


def vsint32_put(chan, val, nnn):
    varint_ = encode_sint32(val)
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[F.V_SINT32] = vsint32_put


def vuint64_put(chan, val, nnn):
    varint_ = 0xffffffffffffffff & val
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[F.V_UINT64] = vuint64_put


def vsint64_put(chan, val, nnn):
    varint_ = encode_sint64(val)
    write_varint_field(chan, varint_, nnn)
T_PUT_FUNCS[F.V_SINT64] = vsint64_put

# -- implemented using B32 --------------------------------


def fuint32_put(chan, val, nnn):
    val = ctypes.c_uint32(val).value
    write_b32_field(chan, val, nnn)
T_PUT_FUNCS[F.F_UINT32] = fuint32_put


def fsint32_put(chan, val, nnn):
    val = ctypes.c_int32(val).value
    write_b32_field(chan, val, nnn)
T_PUT_FUNCS[F.F_SINT32] = fsint32_put


def ffloat_put(chan, val, nnn):
    # @ means native byte order; < would mean little-endian
    v_rep = struct.pack('@f', val)
    varint_ = struct.unpack('@I', v_rep)[0]
    write_b32_field(chan, varint_, nnn)
T_PUT_FUNCS[F.F_FLOAT] = ffloat_put

# -- implemented using B64 --------------------------------


def fuint64_put(chan, val, nnn):
    val = ctypes.c_uint64(val).value
    write_b64_field(chan, val, nnn)
T_PUT_FUNCS[F.F_UINT64] = fuint64_put


def fsint64_put(chan, val, nnn):
    varint_ = ctypes.c_int64(val).value
    write_b64_field(chan, varint_, nnn)
T_PUT_FUNCS[F.F_SINT64] = fsint64_put


def fdouble_put(chan, val, nnn):
    #val = ctypes.c_double(val).value
    v_rep = struct.pack('@d', val)       # this gives us an 8-byte string
    varint_ = struct.unpack('@L', v_rep)[0]
    write_b64_field(chan, varint_, nnn)
T_PUT_FUNCS[F.F_DOUBLE] = fdouble_put                        # END B64


def l_string_put(chan, val, nnn):
    return write_len_plus_field(chan, val.encode('utf-8'), nnn)
T_PUT_FUNCS[F.L_STRING] = l_string_put


def lbytes_put(chan, val, nnn):
    return write_len_plus_field(chan, val, nnn)
T_PUT_FUNCS[F.L_BYTES] = lbytes_put

# XXX NOT GOOD.  val WILL BE DYNAMICALLY DEFINED


def lmsg_put(chan, val, nnn):
    raise NotImplementedError
T_PUT_FUNCS[F.L_MSG] = lmsg_put


def fbytes16_put(chan, val, nnn):
    return write_b128_field(chan, val, nnn)
T_PUT_FUNCS[F.F_BYTES16] = fbytes16_put


def fbytes20_put(chan, val, nnn):
    return write_b160_field(chan, val, nnn)
T_PUT_FUNCS[F.F_BYTES20] = fbytes20_put


def fbytes32_put(chan, val, nnn):
    return write_b256_field(chan, val, nnn)
T_PUT_FUNCS[F.F_BYTES32] = fbytes32_put                # END B256

# GETS ==============================================================

# varint fields -------------------------------------------


def venum_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[F.V_ENUM] = venum_get


def vbool_get(chan):
    varint_ = read_raw_varint(chan)
    if varint_ is True:
        return True
    else:
        return False
T_GET_FUNCS[F.V_BOOL] = vbool_get


def vuint32_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[F.V_UINT32] = vuint32_get


def vsint32_get(chan):
    varint_ = read_raw_varint(chan)
    return decode_sint32(varint_)
T_GET_FUNCS[F.V_SINT32] = vsint32_get


def vuint64_get(chan):
    return read_raw_varint(chan)
T_GET_FUNCS[F.V_UINT64] = vuint64_get


def vsint64_get(chan):
    varint_ = read_raw_varint(chan)
    return decode_sint64(varint_)
T_GET_FUNCS[F.V_SINT64] = vsint64_get              # END VAR

# B32 fields ----------------------------------------------


def fuint32_get(chan):
    return read_raw_b32(chan)
T_GET_FUNCS[F.F_UINT32] = fuint32_get


def fsint32_get(chan):
    return read_raw_b32(chan)
T_GET_FUNCS[F.F_SINT32] = fuint32_get


def ffloat_get(chan):
    val = read_raw_b32(chan)
    # XXX STUB: cast 32-bit val to double
    return val
T_GET_FUNCS[F.F_FLOAT] = ffloat_get

# B64 fields ----------------------------------------------


def fuint64_get(chan):
    return read_raw_b64(chan)
T_GET_FUNCS[F.F_UINT64] = fuint64_get


def fsint64_get(chan):
    return read_raw_b64(chan)
T_GET_FUNCS[F.F_SINT64] = fuint64_get


def fdouble_get(chan):
    val = read_raw_b64(chan)
    # XXX STUB: cast 64-bit val to double
    return val
T_GET_FUNCS[F.F_DOUBLE] = fdouble_get

# LEN_PLUS fields -----------------------------------------


def lstring_get(chan):
    b_array = read_raw_len_plus(chan)
    string = b_array.decode('utf-8')
    # DEBUG
    print("lStringGet '%s' => '%s'" % (b_array, string))
    # END
    return string
T_GET_FUNCS[F.L_STRING] = lstring_get


def lbytes_get(chan):
    return read_raw_len_plus(chan)
T_GET_FUNCS[F.L_BYTES] = lbytes_get


def lmsg_get(chan):
    # caller must interpret the raw byte array
    return read_raw_len_plus(chan)
T_GET_FUNCS[F.L_MSG] = lmsg_get

# other fixed-length byte fields --------------------------


def fbytes16_get(chan):
    return read_raw_b128(chan)
T_GET_FUNCS[F.F_BYTES16] = fbytes16_get


def fbytes20_get(chan):
    return read_raw_b160(chan)
T_GET_FUNCS[F.F_BYTES20] = fbytes20_get


def fbytes32_get(chan):
    return read_raw_b256(chan)
T_GET_FUNCS[F.F_BYTES32] = fbytes32_get


# LEN ===============================================================

def vbool_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_BOOL)
    return len_ + + 1        # header plus one for value
T_LEN_FUNCS[F.V_BOOL] = vbool_len

# XXX This needs some thought


def venum_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_ENUM)
    # XXX we constrain val to this range of non-negative ints
    return len_ + + length_as_varint(val & 0xffff)
T_LEN_FUNCS[F.V_ENUM] = venum_len


def vuint32_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_UINT32)
    # XXX we constrain val to this range of non-negative ints
    return len_ + + length_as_varint(val & 0xffffffff)
T_LEN_FUNCS[F.V_UINT32] = vuint32_len


def vsint32_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_SINT32)
    return len_ + + length_as_varint(encode_sint32(val))
T_LEN_FUNCS[F.V_SINT32] = vsint32_len


def vuint64_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_UINT64)
    # XXX we constrain val to this range of non-negative ints
    return len_ + + length_as_varint(val & 0xffffffffffffffff)
T_LEN_FUNCS[F.V_UINT64] = vuint64_len


def vsint64_len(val, nnn):
    len_ = field_hdr_len(nnn, F.V_SINT64)
    return len_ + + length_as_varint(encode_sint64(val))
T_LEN_FUNCS[F.V_SINT64] = vsint64_len


def fuint32_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_UINT32)
    return len_ + + 4
T_LEN_FUNCS[F.F_UINT32] = fuint32_len


def fsint32_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_SINT32)
    return len_ + + 4
T_LEN_FUNCS[F.F_SINT32] = fsint32_len


def ffloat_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_FLOAT)
    return len_ + + 4
T_LEN_FUNCS[F.F_FLOAT] = ffloat_len


def fuint64_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_UINT64)
    return len_ + + 8
T_LEN_FUNCS[F.F_UINT64] = fuint64_len


def fsint64_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_SINT64)
    return len_ + + 8
T_LEN_FUNCS[F.F_SINT64] = fsint64_len


def fdouble_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_DOUBLE)
    return len_ + + 8
T_LEN_FUNCS[F.F_DOUBLE] = fdouble_len


def l_string_len(val, nnn):
    len_ = field_hdr_len(nnn, F.L_STRING)
    ndx_ = len(val)
    return len_ + + length_as_varint(ndx_) + ndx_
T_LEN_FUNCS[F.L_STRING] = l_string_len


def lbytes_len(val, nnn):
    len_ = field_hdr_len(nnn, F.L_BYTES)
    ndx_ = len(val)
    return len_ + + length_as_varint(ndx_) + ndx_
T_LEN_FUNCS[F.L_BYTES] = lbytes_len


def lmsg_len(val, nnn):
    len_ = field_hdr_len(nnn, F.L_MSG)
    ndx_ = val.wire_len
    return len_ + + length_as_varint(ndx_) + ndx_
T_LEN_FUNCS[F.L_MSG] = lmsg_len


def fbytes16_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_BYTES16)
    return len_ + + 16
T_LEN_FUNCS[F.F_BYTES16] = fbytes16_len


def fbytes20_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_BYTES20)
    return len_ + + 20
T_LEN_FUNCS[F.F_BYTES20] = fbytes20_len


def fbytes32_len(val, nnn):
    len_ = field_hdr_len(nnn, F.F_BYTES32)
    return len_ + + 32
T_LEN_FUNCS[F.F_BYTES32] = fbytes32_len
