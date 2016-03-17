# fieldz/typed.py

import ctypes, struct, sys

import fieldz.fieldTypes    as F
from fieldz.chan            import Channel
from fieldz.raw             import * 

# MsgSpec cannot be imported
#from fieldz.msgSpec import  MsgSpec

__all__ = [\
            'encodeSint32', 'decodeSint32',
            'encodeSint64', 'decodeSint64',
            'notImpl',
            'tPutFuncs',    'tGetFuncs',    'tLenFuncs',
          ]

def encodeSint32(s):
    x = ctypes.c_int32(0xffffffff & s).value
    # we must have the sign filling in from the left
    v = (x << 1) ^ ( x >> 31) 
#   # DEBUG
#   print "\nencodeSint32: 0x%x --> 0x%x" % (s, v)
#   # END
    return v

def decodeSint32(v):
    # decode zig-zag:  stackoverflow 2210923
    x = (v >> 1) ^ (-(v & 1)) 
    s = ctypes.c_int32(x).value
#   # DEBUG
#   print "decodeSint32: 0x%x --> 0x%x" % (v, s)
#   # END
    return s

def encodeSint64(s):
    v = ctypes.c_int64(0xffffffffffffffff & s).value
    # we must have the sign filling in from the left
    v = (v << 1) ^ ( v >> 63) 
    return v

def decodeSint64(v):
    v = (v >> 1) ^ (-(v & 1)) 
    s = ctypes.c_int64(v).value
    return s

# DISPATCH TABLES ===================================================

def notImpl(*arg):     raise NotImplementedError

tPutFuncs = [notImpl]*(F.maxNdx + 1)
tGetFuncs = [notImpl]*(F.maxNdx + 1)
tLenFuncs = [notImpl]*(F.maxNdx + 1)

# puts implemented using varInts --------------------------
def vBoolPut(chan, val, n):
    if val is True:     writeVarintField(chan, 1, n)
    else:               writeVarintField(chan, 0, n)
tPutFuncs[F._V_BOOL]    = vBoolPut

def vEnumPut(chan, val, n):
    # just handle enums as simple ints for now, but constrain
    # to 16 bits; any sign is uhm mangled
    v = 0xffff & val
    writeVarintField(chan, v, n)
tPutFuncs[F._V_ENUM]    = vEnumPut

def vuInt32Put(chan, val, n):
    v = 0xffffffff & val
    writeVarintField(chan, v, n)
tPutFuncs[F._V_UINT32]    = vuInt32Put

def vsInt32Put(chan, val, n):
    v = encodeSint32(val)
    writeVarintField(chan, v, n)
tPutFuncs[F._V_SINT32]    = vsInt32Put

def vuInt64Put(chan, val, n):
    v = 0xffffffffffffffff & val
    writeVarintField(chan, v, n)
tPutFuncs[F._V_UINT64]    = vuInt64Put

def vsInt64Put(chan, val, n):
    v = encodeSint64(val)
    writeVarintField(chan, v, n)  
tPutFuncs[F._V_SINT64]    = vsInt64Put

# -- implemented using B32 --------------------------------
def fuInt32Put(chan, val, n):
    val = ctypes.c_uint32(val).value
    writeB32Field(chan, val, n)
tPutFuncs[F._F_UINT32] = fuInt32Put

def fsInt32Put(chan, val, n):
    val = ctypes.c_int32(val).value
    writeB32Field(chan, val, n)
tPutFuncs[F._F_SINT32] = fsInt32Put

def fFloatPut(chan, val, n):
    # @ means native byte order; < would mean little-endian
    vRep = struct.pack('@f', val)
    v    = struct.unpack('@I',vRep)[0]
    writeB32Field(chan, v, n)
tPutFuncs[F._F_FLOAT] = fFloatPut

# -- implemented using B64 --------------------------------
def fuInt64Put(chan, val, n):
    val = ctypes.c_uint64(val).value
    writeB64Field(chan, val, n)
tPutFuncs[F._F_UINT64] = fuInt64Put

def fsInt64Put(chan, val, n):
    v = ctypes.c_int64(val).value
    writeB64Field(chan, v, n)
tPutFuncs[F._F_SINT64] = fsInt64Put

def fDoublePut(chan, val, n):
    #val = ctypes.c_double(val).value
    vRep = struct.pack('@d', val)       # this gives us an 8-byte string
    v    = struct.unpack('@L',vRep)[0]
    writeB64Field(chan, v, n)
tPutFuncs[F._F_DOUBLE] = fDoublePut                        # END B64

def lStringPut (chan, val, n):
    return  writeLenPlusField(chan, val.encode('utf-8'), n)
tPutFuncs[F._L_STRING] = lStringPut

def lBytesPut (chan, val, n):
    return  writeLenPlusField(chan, val, n)
tPutFuncs[F._L_BYTES] = lBytesPut

# XXX NOT GOOD.  val WILL BE DYNAMICALLY DEFINED
def lMsgPut (chan, val, n):
    raise NotImplementedError
tPutFuncs[F._L_MSG] = lMsgPut

def fBytes16Put (chan, val, n):
    return  writeB128Field(chan, val, n)
tPutFuncs[F._F_BYTES16] = fBytes16Put

def fBytes20Put (chan, val, n):
    return  writeB160Field(chan, val, n)
tPutFuncs[F._F_BYTES20] = fBytes20Put

def fBytes32Put (chan, val, n):
    return  writeB256Field(chan, val, n)
tPutFuncs[F._F_BYTES32] = fBytes32Put                # END B256

# GETS ==============================================================

# varint fields -------------------------------------------
def vEnumGet(chan):
    return readRawVarint(chan)
tGetFuncs[F._V_ENUM] = vEnumGet

def vBoolGet(chan):
    v = readRawVarint(chan)
    if v is True:   return True
    else:           return False
tGetFuncs[F._V_BOOL] = vBoolGet

def vuInt32Get(chan):
    return readRawVarint(chan)
tGetFuncs[F._V_UINT32] = vuInt32Get

def vsInt32Get(chan):
    v = readRawVarint(chan)
    return decodeSint32(v)
tGetFuncs[F._V_SINT32] = vsInt32Get

def vuInt64Get(chan):
    return         readRawVarint(chan)
tGetFuncs[F._V_UINT64] = vuInt64Get

def vsInt64Get(chan):
    v = readRawVarint(chan)
    return decodeSint64(v)
tGetFuncs[F._V_SINT64] = vsInt64Get              # END VAR

# B32 fields ----------------------------------------------
def fuInt32Get(chan):
    return         readRawB32(chan)
tGetFuncs[F._F_UINT32] = fuInt32Get

def fsInt32Get(chan):
    return         readRawB32(chan)
tGetFuncs[F._F_SINT32] = fuInt32Get

def fFloatGet(chan):
    val =  readRawB32(chan)
    # XXX STUB: cast 32-bit val to double
    return val
tGetFuncs[F._F_FLOAT] = fFloatGet

# B64 fields ----------------------------------------------
def fuInt64Get(chan):
    return         readRawB64(chan)
tGetFuncs[F._F_UINT64] = fuInt64Get

def fsInt64Get(chan):
    return         readRawB64(chan)
tGetFuncs[F._F_SINT64] = fuInt64Get

def fDoubleGet(chan):
    val =  readRawB64(chan)
    # XXX STUB: cast 64-bit val to double
    return val
tGetFuncs[F._F_DOUBLE] = fDoubleGet

# LEN_PLUS fields -----------------------------------------
def lStringGet(chan):
    bArray = readRawLenPlus(chan)
    s = bArray.decode('utf-8')
    # DEBUG
    print("lStringGet '%s' => '%s'" % (bArray, s))
    # END
    return s
tGetFuncs[F._L_STRING] = lStringGet

def lBytesGet(chan):
    return readRawLenPlus(chan)
tGetFuncs[F._L_BYTES] = lBytesGet

def lMsgGet(chan):
    # caller must interpret the raw byte array
    return readRawLenPlus(chan)
tGetFuncs[F._L_MSG] = lMsgGet

# other fixed-length byte fields --------------------------
def fBytes16Get(chan):
    return readRawB128(chan)
tGetFuncs[F._F_BYTES16] = fBytes16Get

def fBytes20Get(chan):
    return readRawB160(chan)
tGetFuncs[F._F_BYTES20] = fBytes20Get

def fBytes32Get(chan):
    return readRawB256(chan)
tGetFuncs[F._F_BYTES32] = fBytes32Get


# LEN =============================================================== 

def vBoolLen(val, n):
    h = fieldHdrLen(n, F._V_BOOL)
    return h + 1        # header plus one for value
tLenFuncs[F._V_BOOL] = vBoolLen

# XXX This needs some thought
def vEnumLen(val, n):
    h = fieldHdrLen(n, F._V_ENUM)
    # XXX we constrain val to this range of non-negative ints
    return h + lengthAsVarint( val & 0xffff)
tLenFuncs[F._V_ENUM] = vEnumLen

def vuInt32Len(val, n):
    h = fieldHdrLen(n, F._V_UINT32)
    # XXX we constrain val to this range of non-negative ints
    return h + lengthAsVarint(val & 0xffffffff)
tLenFuncs[F._V_UINT32] = vuInt32Len

def vsInt32Len(val, n):
    h = fieldHdrLen(n, F._V_SINT32)
    return h + lengthAsVarint(encodeSint32(val))
tLenFuncs[F._V_SINT32] = vsInt32Len

def vuInt64Len(val, n):
    h = fieldHdrLen(n, F._V_UINT64)
    # XXX we constrain val to this range of non-negative ints
    return h + lengthAsVarint(val & 0xffffffffffffffff)
tLenFuncs[F._V_UINT64] = vuInt64Len

def vsInt64Len(val, n):
    h = fieldHdrLen(n, F._V_SINT64)
    return h + lengthAsVarint(encodeSint64(val))
tLenFuncs[F._V_SINT64] = vsInt64Len

def fuInt32Len(val, n):
    h = fieldHdrLen(n, F._F_UINT32)
    return h + 4
tLenFuncs[F._F_UINT32] = fuInt32Len

def fsInt32Len(val, n):
    h = fieldHdrLen(n, F._F_SINT32)
    return h + 4
tLenFuncs[F._F_SINT32] = fsInt32Len

def fFloatLen(val, n):
    h = fieldHdrLen(n, F._F_FLOAT)
    return h + 4
tLenFuncs[F._F_FLOAT] = fFloatLen

def fuInt64Len(val, n):
    h = fieldHdrLen(n, F._F_UINT64)
    return h + 8
tLenFuncs[F._F_UINT64] = fuInt64Len

def fsInt64Len(val, n):
    h = fieldHdrLen(n, F._F_SINT64)
    return h + 8
tLenFuncs[F._F_SINT64] = fsInt64Len

def fDoubleLen(val, n):
    h = fieldHdrLen(n, F._F_DOUBLE)
    return h + 8
tLenFuncs[F._F_DOUBLE] = fDoubleLen

def lStringLen(val,n):
    h = fieldHdrLen(n, F._L_STRING)
    x = len(val)
    return h + lengthAsVarint(x) + x
tLenFuncs[F._L_STRING] = lStringLen

def lBytesLen(val, n):
    h = fieldHdrLen(n, F._L_BYTES)
    x = len(val)
    return h + lengthAsVarint(x) + x
tLenFuncs[F._L_BYTES] = lBytesLen

def lMsgLen(val, n):
    h = fieldHdrLen(n, F._L_MSG)
    x = val.wireLen 
    return h + lengthAsVarint(x) + x
tLenFuncs[F._L_MSG] = lMsgLen

def fBytes16Len(val, n):
    h = fieldHdrLen(n, F._F_BYTES16)
    return h + 16
tLenFuncs[F._F_BYTES16] = fBytes16Len

def fBytes20Len(val, n):
    h = fieldHdrLen(n, F._F_BYTES20)
    return h + 20
tLenFuncs[F._F_BYTES20] = fBytes20Len

def fBytes32Len(val, n):
    h = fieldHdrLen(n, F._F_BYTES32)
    return h + 32
tLenFuncs[F._F_BYTES32] = fBytes32Len

