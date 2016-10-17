# fieldz/raw.py

import ctypes
from fieldz.field_types import FieldTypes as F, FieldStr as FS

# for debugging
#import binascii

__all__ = [
    'VARINT_TYPE', 'PACKED_VARINT_TYPE',
    'B32_TYPE', 'B64_TYPE', 'LEN_PLUS_TYPE',
    'B128_TYPE', 'B160_TYPE', 'B256_TYPE',

    'fieldHdr', 'readFieldHdr', 'fieldHdrLen',
    'hdrFieldNbr', 'hdrType',
    'lengthAsVarint', 'writeVarintField',
    'readRawVarint', 'writeRawVarint',
    'readRawB32', 'writeB32Field',
    'readRawB64', 'writeB64Field',
    'readRawLenPlus', 'writeLenPlusField',
    'readRawB128', 'writeB128Field',
    'readRawB160', 'writeB160Field',
    'readRawB256', 'writeB256Field',
    # -- methods --------------------------------------------
    'nextPowerOfTwo',
    # -- classes --------------------------------------------
    'WireBuffer',
]

# these are PRIMITIVE types, which determine the number of bytes
# occupied in the buffer; they are NOT data types
VARINT_TYPE = 0  # variable length integer
PACKED_VARINT_TYPE = 1  # variable length integer
B32_TYPE = 2  # fixed length, 32 bits
B64_TYPE = 3  # fixed length, 64 bits
LEN_PLUS_TYPE = 4  # sequence of bytes preceded by a varint length
B128_TYPE = 5  # fixed length, 128 bits (AES IV length)
B160_TYPE = 6  # fixed length, 160 bits (SHA1 content key)
B256_TYPE = 7  # fixed length, 128 bits (SHA3 content key)

# FIELD HEADERS #####################################################


def fieldHdr(n, t):
    # it would be prudent but slower to validate the parameters
    # DEBUG
    #   print "n = %u, t = %u, header is 0x%x" % (n, t, (n << 3) | t)
    # END
    return (n << 3) | t


def fieldHdrLen(n, t):
    return lengthAsVarint(fieldHdr(n, t))


def hdrFieldNbr(h):
    return h >> 3


def hdrType(h):
    return h & 7


def readFieldHdr(chan):
    hdr = readRawVarint(chan)
    pType = hdrType(hdr)      # this is the primitive field type
    fieldNbr = hdrFieldNbr(hdr)
    return (pType, fieldNbr)

# VARINTS ###########################################################


def lengthAsVarint(v):
    """
    Return the number of bytes occupied by an unsigned int.
    caller is responsible for assuring that v is in fact properly
    cast as unsigned occupying no more space than an int64 (and
    so no more than 10 bytes).
    """
    if v < (1 << 7):
        return 1
    elif v < (1 << 14):
        return 2
    elif v < (1 << 21):
        return 3
    elif v < (1 << 28):
        return 4
    elif v < (1 << 35):
        return 5
    elif v < (1 << 42):
        return 6
    elif v < (1 << 49):
        return 7
    elif v < (1 << 56):
        return 8
    elif v < (1 << 63):
        return 9
    else:
        return 10


def readRawVarint(chan):
    buf = chan.buffer
    offset = chan.position
    v = 0
    x = 0
    while True:
        if offset >= len(buf):
            raise ValueError("attempt to read beyond end of buffer")
        nextByte = buf[offset]
        offset += 1

        sign = nextByte & 0x80
        nextByte = nextByte & 0x7f
        nextByte <<= (x * 7)
        v |= nextByte
        x += 1

        if sign == 0:
            break
    chan.position = offset
    return v


def writeRawVarint(chan, s):
    buf = chan.buffer
    offset = chan.position
    # all varints are construed as 64 bit unsigned numbers
    v = ctypes.c_uint64(s).value
#   # DEBUG
#   print "entering writeRaw: will write 0x%x at offset %u" % ( v, offset)
#   # END
    l = lengthAsVarint(v)
    if offset + l > len(buf):
        raise ValueError("can't fit varint of length %u into buffer" % l)
    while True:
        buf[offset] = (v & 0x7f)
        offset += 1
        v >>= 7
        if v == 0:
            chan.position = offset   # next unused byte
            break
        else:
            buf[offset - 1] |= 0x80


def writeVarintField(chan, v, n):
    # the header is the field number << 3 ORed with 0, VARINT_TYPE
    hdr = fieldHdr(n, VARINT_TYPE)
    writeRawVarint(chan, hdr)
#   # DEBUG
#   print "header was 0x%x; writing value 0x%x at offset %u" % (
#                                               hdr, v, chan.position)
#   # END
    writeRawVarint(chan, v)

# 32- AND 64-BIT FIXED LENGTH FIELDS ################################


def readRawB32(chan):
    """ buf construed as array of unsigned bytes """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    v = buf[offset]
    offset += 1         # little-endian
    v |= buf[offset] << 8
    offset += 1
    v |= buf[offset] << 16
    offset += 1
    v |= buf[offset] << 24
    offset += 1
    chan.position = offset
    return v


def writeRawB32(chan, v):
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    offset += 1
    chan.position = offset


def writeB32Field(chan, v, f):
    hdr = fieldHdr(f, B32_TYPE)
    writeRawVarint(chan, hdr)
    writeRawB32(chan, v)


def readRawB64(chan):
    """ buf construed as array of unsigned bytes """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    v = buf[offset]
    offset += 1         # little-endian
    v |= buf[offset] << 8
    offset += 1
    v |= buf[offset] << 16
    offset += 1
    v |= buf[offset] << 24
    offset += 1
    v |= buf[offset] << 32
    offset += 1
    v |= buf[offset] << 40
    offset += 1
    v |= buf[offset] << 48
    offset += 1
    v |= buf[offset] << 56
    offset += 1
    chan.position = offset
    return v


def writeRawB64(chan, v):
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    v >>= 8
    offset += 1
    buf[offset] = 0xff & v
    offset += 1
    chan.position = offset


def writeB64Field(chan, v, f):
    hdr = fieldHdr(f, B64_TYPE)
    writeRawVarint(chan, hdr)
    writeRawB64(chan, v)

# VARIABLE LENGTH FIELDS ############################################


def readRawLenPlus(chan):

    # read the varint len
    n = readRawVarint(chan)
    buf = chan.buffer
    offset = chan.position

#   # DEBUG
#   print "readRawLenPlus: length of text is %d bytes" % n
#   # END

    # then read n actual bytes
    s = []
    count = 0
    while count < n:
        s.append(buf[offset])
        count += 1
        offset += 1
    chan.position = offset
    return bytearray(s)


def writeRawBytes(chan, bytes):
    """ bytes a byte array """
    buf = chan.buffer
    offset = chan.position
    # XXX CHECK LEN OFFSET

    # DEBUG
    print("writeRawBytes: type(bytes) is ", type(bytes))
    # END

    for b in bytes:
        buf[offset] = int(b)
        offset += 1
#   # DEBUG
#   print "wrote '%s' as %u raw bytes" % (str(bytes), len(bytes))
#   # END
    chan.position = offset

# XXX 2012-12-11 currently used only in one place


def writeFieldHdr(chan, fieldNbr, primType):
    """ write the field header """
    hdr = fieldHdr(fieldNbr, primType)
    writeRawVarint(chan, hdr)


def writeLenPlusField(chan, s, f):
    """s is a bytearray or string"""
    writeFieldHdr(chan, f, LEN_PLUS_TYPE)
    # write the length of the byte array --------
    writeRawVarint(chan, len(s))

    # now write the byte array itself -----------
    writeRawBytes(chan, s)

# LONGER FIXED-LENGTH BYTE FIELDS ===================================


def readRawB128(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    s = []
    for i in range(16):
        s.append(buf[offset + i])
    offset += 16
    chan.position = offset
    return bytearray(s)


def writeRawB128(chan, v):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    for i in range(16):
        # this is a possibly unnecessary cast
        buf[offset] = 0xff & v[i]
        offset += 1
    chan.position = offset


def writeB128Field(chan, v, f):
    hdr = fieldHdr(f, B128_TYPE)
    writeRawVarint(chan, hdr)
    writeRawB128(chan, v)                  # GEEP


def readRawB160(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    s = []
    for i in range(20):
        s.append(buf[offset + i])
    offset += 20
    chan.position = offset
    return bytearray(s)


def writeRawB160(chan, v):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    for i in range(20):
        buf[offset] = v[i]
        offset += 1
    chan.position = offset


def writeB160Field(chan, v, f):
    hdr = fieldHdr(f, B160_TYPE)
    writeRawVarint(chan, hdr)
    writeRawB160(chan, v)                  # GEEP


def readRawB256(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    s = []
    for i in range(32):
        s.append(buf[offset + i])
    offset += 32
    chan.position = offset
    return bytearray(s)


def writeRawB256(chan, v):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    # DEBUG
    # print "DEBUG: writeRawB256 datum len is %s" % len(v)
    # END
    for i in range(32):
        # print "DEBUG:    v[%u] = %s" % (i, binascii.b2a_hex(v[i]))
        buf[offset] = v[i]
        offset += 1
    chan.position = offset


def writeB256Field(chan, v, f):
    hdr = fieldHdr(f, B256_TYPE)
    writeRawVarint(chan, hdr)
    writeRawB256(chan, v)                  # GEEP

# PRIMITIVE FIELD NAMES =============================================


class PrimFields(object):
    """ lower-level primitive field types """

    _P_VARINT = 0
    _P_B32 = 1     # 32 bit fields
    _P_B64 = 2     # 64 bit fields
    _P_LEN_PLUS = 3     # varint len followed by that many bytes
    # the following can be implemented in terms of _P_LEN_PLUS
    _P_B128 = 4    # fixed length string of 16 bytes
    _P_B160 = 5    # fixed length string of 20 bytes
    _P_B256 = 6    # fixed length string of 32 bytes

    _MAX_TYPE = _P_B256

    # none of these (pVarint..pB256) is currently used
#   @property
#   def pVarint(clz):       return clz._P_VARINT
#   @property
#   def pB32(clz):          return clz._P_B32
#   @property
#   def pB64(clz):          return clz._P_B64
#   @property
#   def pLenPlus(clz):      return clz._P_LenPlus
#   @property
#   def pB128(clz):         return clz._P_B128
#   @property
#   def pB160(clz):         return clz._P_B160
#   @property
#   def pB256(clz):         return clz._P_B256

    _names = {}
    _names[_P_VARINT] = 'pVarint'
    _names[_P_B32] = 'pB32'
    _names[_P_B64] = 'pB64'
    _names[_P_LEN_PLUS] = 'pLenPlus'
    _names[_P_B128] = 'pB128'
    _names[_P_B160] = 'pB160'
    _names[_P_B256] = 'pB256'

    @classmethod
    def name(clz, v):
        if v is None or v < 0 or FieldTypes._MAX_TYPE < v:
            raise ValueError('no such field type: %s' + str(v))
        return clz._names[v]

# -- WireBuffer -----------------------------------------------------


def nextPowerOfTwo(n):
    """
    If n is a power of two, return n.  Otherwise return the next
    higher power of 2.
    See eg http://acius2.blogspot.com/2007/11/calculating-next-power-of-2.html
    """
    if n < 1:
        raise ValueError("nextPowerOfTwo: %s < 1" % str(n))
    n = n - 1
    n = (n >> 1) | n
    n = (n >> 2) | n
    n = (n >> 4) | n
    n = (n >> 8) | n
    n = (n >> 16) | n
    return n + 1


class WireBuffer(object):

    __slots__ = ['_buffer', '_capacity', '_limit', '_position', ]

    def __init__(self, n=1024, buffer=None):
        """
        Initialize the object.  If a buffer is specified, use it.
        Otherwise create one.  The resulting buffer will have a
        capacity which is a power of 2.
        """
        if buffer:
            self._buffer = buffer
            bufSize = len(buffer)
            if n < bufSize:
                n = bufSize
            n = nextPowerOfTwo(n)
            # DANGER: buffer capacities of cloned buffers can get out of sync
            if n > bufSize:
                more = bytearray(n - bufSize)
                self.buffer.extend(more)
        else:
            n = nextPowerOfTwo(n)
            # allocate and initialize the buffer; init probably a waste of time
            self._buffer = bytearray(n)

        self._capacity = n
        self._limit = n
        self._position = 0

    def copy(self):
        """
        Returns a copy of this WireBuffer using the same underlying
        bytearray.
        """
        return WireBuffer(len(self._buffer), self._buffer)

    @property
    def buffer(self): return self._buffer

    @property
    def position(self): return self._position

    @position.setter
    def position(self, offset):
        if offset < 0:
            raise ValueError('position cannot be negative')
        if (offset >= len(self._buffer)):
            raise ValueError('position cannot be beyond capacity')
        self._position = offset

    @property
    def limit(self): return self._limit

    @limit.setter
    def limit(self, offset):
        if offset < 0:
            raise ValueError('limit cannot be set to a negative')
        if (offset < self._position):
            raise ValueError(
                "limit can't be set to less than current position")
        if (offset > self._capacity):
            raise ValueError('limit cannot be beyond capacity')
        self._limit = offset

    @property
    def capacity(self):
        return len(self._buffer)

    def reserve(self, k):
        """
        We need to add k more bytes; if the buffer isn't big enough,
        resize it.
        """
        if k < 0:
            raise ValueError(
                "attempt to increase WireBuffer size by negative number of bytes")
        if self._position + k >= self._capacity:
            # wildly inefficient, I'm sure
            more = bytearray(self._capacity)
            self._buffer.extend(more)
            self._capacity *= 2
