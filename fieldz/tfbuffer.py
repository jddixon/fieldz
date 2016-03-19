# fieldz/tfbuffer.py

import ctypes
import sys

import fieldz.chan
from fieldz.msgSpec import MsgSpec
from fieldz.raw import *
from fieldz.typed import tPutFuncs, tGetFuncs, tLenFuncs

import fieldz.fieldTypes as F

__all__ = [\
    # value uncertain
    'TFBuffer', 'TFReader', 'TFWriter',
]

# -- CLASSES --------------------------------------------------------


class TFBuffer(fieldz.chan.Channel):

    __slots__ = [ \
        # '_buffer',
        '_msgSpec', ]

    def __init__(self, msgSpec, n=1024, buffer=None):
        super(TFBuffer, self).__init__(n, buffer)
        if msgSpec is None:
            raise ValueError('no msgSpec')
        if not isinstance(msgSpec, MsgSpec):
            raise ValueError('object is not a MsgSpec')
        self._msgSpec = msgSpec

    @classmethod
    def create(cls, msgSpec, n):
        if n <= 0:
            raise ValueError("buffer size must be a positive number")
        buffer = bytearray(n)
        return cls(msgSpec, n, buffer)


class TFReader(TFBuffer):
    # needs some thought; the pType is for debug
    __slots__ = ['_fieldNbr', '_fType', '_pType', '_value', ]

    def __init(self, msgSpec, n, buffer):
        #super(TFReader, self).__init__(msgSpec, len(buffer), buffer)
        super(TFReader, self).__init__(msgSpec, n, buffer)
        # this is a decision: we could read the first field
        self._fieldNbr = -1
        self._fType = -1
        self._pType = -1
        self._value = None

    # def create(n) inherited

    @property
    def fieldNbr(self): return self._fieldNbr

    @property
    def fType(self): return self._fType

    @property
    def pType(self): return self._pType      # for DEBUG

    @property
    def value(self): return self._value

    def getNext(self):
        (self._pType, self._fieldNbr) = readFieldHdr(self)

        # getter has range check
        fType = self._fType = self._msgSpec.fTypeNdx(self._fieldNbr)

        # gets through dispatch table -------------------------------
        if 0 <= fType and fType <= F._V_SINT64:
            self._value = tGetFuncs[fType](self)
            return

        # we use the field type to verify that have have read the right
        # primitive type
#       # - implemented using varints -------------------------------
#       if self._fType <= F._V_UINT64:
#           if self._pType != VARINT_TYPE:
#               raise RuntimeError("pType is %u but should be %u" % (
#                                       self._pType, VARINT_TYPE))
#           (self._value, self._position) = readRawVarint(
#                                           self)
#           # DEBUG
#           print "getNext: readRawVarint returns value = 0x%x" % self._value
#           # END
#           if self._fType == F._V_SINT32:
#               self._value = decodeSint32(self._value)
#               # DEBUG
#               print "    after decode self._value is 0x%x" % self._value
#               #
#           elif self._fType == F._V_SINT64:
#               self._value = decodeSint64(self._value)

#           #END VARINT_GET

        # implemented using B32 -------------------------------------
        if self._fType <= F._F_FLOAT:
            self._pType = B32_TYPE              # DEBUG
            v = readRawB32(self)
            if self._fType == F._F_UINT32:
                self._value = ctypes.c_uint32(v).value
            elif self._fType == F._F_SINT32:
                self._value = ctypes.c_int32(v).value
            else:
                raise NotImplementedError('B32 handling for float')

        # implemented using B64 -------------------------------------
        elif self._fType <= F._F_DOUBLE:
            self._pType = B64_TYPE              # DEBUG
            (v, self._position) = readRawB64(self)
            if self._fType == F._F_UINT64:
                self._value = ctypes.c_uint64(v).value
            elif self._fType == F._F_SINT64:
                self._value = ctypes.c_int64(v).value
            else:
                raise NotImplementedError('B64 handling for double')

        # implemented using LEN_PLUS --------------------------------
        elif self._fType <= F._L_MSG:
            self._pType = LEN_PLUS_TYPE         # DEBUG
            v = readRawLenPlus(self)
            if self._fType == F._L_STRING:
                self._value = v.decode('utf-8')
            elif self._fType == F._L_BYTES:
                self._value = v
            else:
                raise NotImplementedError('LEN_PLUS handled as L_MSG')

        # implemented using B128, B160, B256 ------------------------
        elif self._fType == F._F_BYTES16:
            self._pType = B128_TYPE             # DEBUG
            self._value = readRawB128(self)
        elif self._fType == F._F_BYTES20:
            self._pType = B160_TYPE             # DEBUG
            self._value = readRawB160(self)
        elif self._fType == F._F_BYTES32:
            self._pType = B256_TYPE             # DEBUG
            self._value = readRawB256(self)

        else:
            raise NotImplementedError(
                "decode for type %d has not been implemented" % self._fType)

        # END GET


class TFWriter(TFBuffer):
    # needs some thought; MOSTLY FOR DEBUG
    __slots__ = ['_fieldNbr', '_fType', '_pType', '_value', ]

    def __init(self, msgSpec, n=1024, buffer=None):
        super(TFWriter, self).__init__(msgSpec, n, buffer)
        # this is a decision: we could read the first field
        self._fieldNbr = -1
        self._fType = -1
        self._pType = -1
        self._value = None

    # def create(n) inherited

    # These are for DEBUG
    @property
    def fieldNbr(self): return self._fieldNbr

    @property
    def fType(self): return self._fType

    @property
    def pType(self): return self._pType

    @property
    def value(self): return self._value
    # END DEBUG PROPERTIES

    def putNext(self, fieldNbr, value):

        # getter has range check
        fType = self._msgSpec.fTypeNdx(fieldNbr)

        # puts through dispatch table -------------------------------
        if 0 <= fType and fType <= F._F_BYTES32:
            # DEBUG
            print("putNext: field type is %d (%s)" % (fType, F.asStr(fType)))
            sys.stdout.flush()
            # END
            tPutFuncs[fType](self, value, fieldNbr)
            # DEBUG
            if fType < F._L_STRING:
                print("putNext through dispatch table:\n"
                      "         field   %u\n"
                      "         fType   %u,  %s\n"
                      "         value   %d (0x%x)\n"
                      "         offset  %u" % (
                          fieldNbr, fType, F.asStr(fType),
                          value, value, self._position))
            # END
            return
        else:
            print("unknown/unimplemented field type %s" % str(fType))

        # -- NOW VESTIGIAL ------------------------------------------
        v = None
