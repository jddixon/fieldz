# fieldz/raw.py

import ctypes
from fieldz.field_types import FieldTypes

# for debugging
#import binascii

__all__ = [
    'VARINT_TYPE', 'PACKED_VARINT_TYPE',
    'B32_TYPE', 'B64_TYPE', 'LEN_PLUS_TYPE',
    'B128_TYPE', 'B160_TYPE', 'B256_TYPE',

    'field_hdr', 'read_field_hdr', 'field_hdr_len',
    'hdr_field_nbr', 'hdr_type',
    'length_as_varint', 'write_varint_field',
    'read_raw_varint', 'write_raw_varint',
    'read_raw_b32', 'write_b32_field',
    'read_raw_b64', 'write_b64_field',
    'read_raw_len_plus', 'write_len_plus_field',
    'read_raw_b128', 'write_b128_field',
    'read_raw_b160', 'write_b160_field',
    'read_raw_b256', 'write_b256_field',
    # -- methods --------------------------------------------
    'next_power_of_two',
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


def field_hdr(ndx, tstamp):
    # it would be prudent but slower to validate the parameters
    # DEBUG
    #   print "ndx = %u, t = %u, header is 0x%x" % (n, t, (n << 3) | t)
    # END
    return (ndx << 3) | tstamp


def field_hdr_len(nnn, tstamp):
    return length_as_varint(field_hdr(nnn, tstamp))


def hdr_field_nbr(ndx):
    return ndx >> 3


def hdr_type(ndx):
    return ndx & 7


def read_field_hdr(chan):
    hdr = read_raw_varint(chan)
    p_type = hdr_type(hdr)      # this is the primitive field type
    field_nbr = hdr_field_nbr(hdr)
    return (p_type, field_nbr)

# VARINTS ###########################################################


def length_as_varint(varint_):
    """
    Return the number of bytes occupied by an unsigned int.
    caller is responsible for assuring that v is in fact properly
    cast as unsigned occupying no more space than an int64 (and
    so no more than 10 bytes).
    """
    if varint_ < (1 << 7):
        return 1
    elif varint_ < (1 << 14):
        return 2
    elif varint_ < (1 << 21):
        return 3
    elif varint_ < (1 << 28):
        return 4
    elif varint_ < (1 << 35):
        return 5
    elif varint_ < (1 << 42):
        return 6
    elif varint_ < (1 << 49):
        return 7
    elif varint_ < (1 << 56):
        return 8
    elif varint_ < (1 << 63):
        return 9
    else:
        return 10


def read_raw_varint(chan):
    buf = chan.buffer
    offset = chan.position
    varint_ = 0
    ndx_ = 0
    while True:
        if offset >= len(buf):
            raise ValueError("attempt to read beyond end of buffer")
        next_byte = buf[offset]
        offset += 1

        sign = next_byte & 0x80
        next_byte = next_byte & 0x7f
        next_byte <<= (ndx_ * 7)
        varint_ |= next_byte
        ndx_ += 1

        if sign == 0:
            break
    chan.position = offset
    return varint_


def write_raw_varint(chan, string):
    buf = chan.buffer
    offset = chan.position
    # all varints are construed as 64 bit unsigned numbers
    varint_ = ctypes.c_uint64(string).value
#   # DEBUG
#   print "entering writeRaw: will write 0x%x at offset %u" % ( v, offset)
#   # END
    len_ = length_as_varint(varint_)
    if offset + len_ > len(buf):
        raise ValueError("can't fit varint of length %u into buffer" % len_)
    while True:
        buf[offset] = (varint_ & 0x7f)
        offset += 1
        varint_ >>= 7
        if varint_ == 0:
            chan.position = offset   # next unused byte
            break
        else:
            buf[offset - 1] |= 0x80


def write_varint_field(chan, varint_, nnn):
    # the header is the field number << 3 ORed with 0, VARINT_TYPE
    hdr = field_hdr(nnn, VARINT_TYPE)
    write_raw_varint(chan, hdr)
#   # DEBUG
#   print "header was 0x%x; writing value 0x%x at offset %u" % (
#                                               hdr, v, chan.position)
#   # END
    write_raw_varint(chan, varint_)

# 32- AND 64-BIT FIXED LENGTH FIELDS ################################


def read_raw_b32(chan):
    """ buf construed as array of unsigned bytes """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    varint_ = buf[offset]
    offset += 1         # little-endian
    varint_ |= buf[offset] << 8
    offset += 1
    varint_ |= buf[offset] << 16
    offset += 1
    varint_ |= buf[offset] << 24
    offset += 1
    chan.position = offset
    return varint_


def write_raw_b32(chan, varint_):
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    offset += 1
    chan.position = offset


def write_b32_field(chan, varint_, file):
    hdr = field_hdr(file, B32_TYPE)
    write_raw_varint(chan, hdr)
    write_raw_b32(chan, varint_)


def read_raw_b64(chan):
    """ buf construed as array of unsigned bytes """
    buf = chan.buffer
    offset = chan.position
    # XXX verify buffer long enough
    varint_ = buf[offset]
    offset += 1         # little-endian
    varint_ |= buf[offset] << 8
    offset += 1
    varint_ |= buf[offset] << 16
    offset += 1
    varint_ |= buf[offset] << 24
    offset += 1
    varint_ |= buf[offset] << 32
    offset += 1
    varint_ |= buf[offset] << 40
    offset += 1
    varint_ |= buf[offset] << 48
    offset += 1
    varint_ |= buf[offset] << 56
    offset += 1
    chan.position = offset
    return varint_


def write_raw_b64(chan, varint_):
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    varint_ >>= 8
    offset += 1
    buf[offset] = 0xff & varint_
    offset += 1
    chan.position = offset


def write_b64_field(chan, varint_, file):
    hdr = field_hdr(file, B64_TYPE)
    write_raw_varint(chan, hdr)
    write_raw_b64(chan, varint_)

# VARIABLE LENGTH FIELDS ############################################


def read_raw_len_plus(chan):

    # read the varint len
    len_ = read_raw_varint(chan)
    buf = chan.buffer
    offset = chan.position

#   # DEBUG
#   print "readRawLenPlus: length of text is %d bytes" % len_
#   # END

    # then read n actual bytes
    string = []
    count = 0
    while count < len_:
        string.append(buf[offset])
        count += 1
        offset += 1
    chan.position = offset
    return bytearray(string)


def write_raw_bytes(chan, bytes_):
    """ bytes a byte array """
    buf = chan.buffer
    offset = chan.position
    # XXX CHECK LEN OFFSET

    # DEBUG
    print("writeRawBytes: type(bytes) is ", type(bytes_))
    # END

    for b_val in bytes_:
        buf[offset] = int(b_val)
        offset += 1
#   # DEBUG
    print("wrote '%s' as %u raw bytes" % (str(bytes_), len(bytes_)))
#   # END
    chan.position = offset

# XXX 2012-12-11 currently used only in one place


def write_field_hdr(chan, field_nbr, prim_type):
    """ write the field header """
    hdr = field_hdr(field_nbr, prim_type)
    write_raw_varint(chan, hdr)


def write_len_plus_field(chan, string, file):
    """s is a bytearray or string"""
    write_field_hdr(chan, file, LEN_PLUS_TYPE)
    # write the length of the byte array --------
    write_raw_varint(chan, len(string))

    # now write the byte array itself -----------
    write_raw_bytes(chan, string)

# LONGER FIXED-LENGTH BYTE FIELDS ===================================


def read_raw_b128(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(16):
        string.append(buf[offset + i])
    offset += 16
    chan.position = offset
    return bytearray(string)


def write_raw_b128(chan, varint_):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    for i in range(16):
        # this is a possibly unnecessary cast
        buf[offset] = 0xff & varint_[i]
        offset += 1
    chan.position = offset


def write_b128_field(chan, varint_, file):
    hdr = field_hdr(file, B128_TYPE)
    write_raw_varint(chan, hdr)
    write_raw_b128(chan, varint_)                  # GEEP


def read_raw_b160(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(20):
        string.append(buf[offset + i])
    offset += 20
    chan.position = offset
    return bytearray(string)


def write_raw_b160(chan, varint_):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    for i in range(20):
        buf[offset] = varint_[i]
        offset += 1
    chan.position = offset


def write_b160_field(chan, varint_, file):
    hdr = field_hdr(file, B160_TYPE)
    write_raw_varint(chan, hdr)
    write_raw_b160(chan, varint_)                  # GEEP


def read_raw_b256(chan):
    """ buf construed as array of unsigned bytes """
    # XXX verify buffer long enough
    buf = chan.buffer
    offset = chan.position
    string = []
    for i in range(32):
        string.append(buf[offset + i])
    offset += 32
    chan.position = offset
    return bytearray(string)


def write_raw_b256(chan, varint_):
    """ v is a bytearray or string """
    buf = chan.buffer
    offset = chan.position
    # DEBUG
    # print "DEBUG: writeRawB256 datum len is %s" % len(v)
    # END
    for i in range(32):
        # print "DEBUG:    v[%u] = %s" % (i, binascii.b2a_hex(v[i]))
        buf[offset] = varint_[i]
        offset += 1
    chan.position = offset


def write_b256_field(chan, varint_, file):
    hdr = field_hdr(file, B256_TYPE)
    write_raw_varint(chan, hdr)
    write_raw_b256(chan, varint_)                  # GEEP

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
    def name(cls, varint_):
        if varint_ is None or varint_ < 0 or FieldTypes._MAX_TYPE < varint_:
            raise ValueError('no such field type: %s' + str(varint_))
        return cls._names[varint_]

# -- WireBuffer -----------------------------------------------------


def next_power_of_two(nnn):
    """
    If n is a power of two, return n.  Otherwise return the next
    higher power of 2.
    See eg http://acius2.blogspot.com/2007/11/calculating-next-power-of-2.html
    """
    if nnn < 1:
        raise ValueError("nextPowerOfTwo: %s < 1" % str(nnn))
    nnn = nnn - 1
    nnn = (nnn >> 1) | nnn
    nnn = (nnn >> 2) | nnn
    nnn = (nnn >> 4) | nnn
    nnn = (nnn >> 8) | nnn
    nnn = (nnn >> 16) | nnn
    return nnn + 1


class WireBuffer(object):

    __slots__ = ['_buffer', '_capacity', '_limit', '_position', ]

    def __init__(self, nnn=1024, buffer=None):
        """
        Initialize the object.  If a buffer is specified, use it.
        Otherwise create one.  The resulting buffer will have a
        capacity which is a power of 2.
        """
        if buffer:
            self._buffer = buffer
            buf_size = len(buffer)
            if nnn < buf_size:
                nnn = buf_size
            nnn = next_power_of_two(nnn)
            # DANGER: buffer capacities of cloned buffers can get out of sync
            if nnn > buf_size:
                more = bytearray(nnn - buf_size)
                self.buffer.extend(more)
        else:
            nnn = next_power_of_two(nnn)
            # allocate and initialize the buffer; init probably a waste of time
            self._buffer = bytearray(nnn)

        self._capacity = nnn
        self._limit = nnn
        self._position = 0

    def copy(self):
        """
        Returns a copy of this WireBuffer using the same underlying
        bytearray.
        """
        return WireBuffer(len(self._buffer), self._buffer)

    @property
    def buffer(self):
        return self._buffer

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, offset):
        if offset < 0:
            raise ValueError('position cannot be negative')
        if offset >= len(self._buffer):
            raise ValueError('position cannot be beyond capacity')
        self._position = offset

    @property
    def limit(self):
        return self._limit

    @limit.setter
    def limit(self, offset):
        if offset < 0:
            raise ValueError('limit cannot be set to a negative')
        if offset < self._position:
            raise ValueError(
                "limit can't be set to less than current position")
        if offset > self._capacity:
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
