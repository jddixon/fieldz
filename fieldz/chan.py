# ~/dev/py/fieldz/fieldz/chan.py

__all__ = ['Channel',
          ]

# XXX COMPARE WITH Java ByteBuffer

# -- Channel -----------------------------------------------------
class Channel(object):
   
    __slots__ = ['_buffer', '_capacity', '_limit', '_position', ]

    def __init__(self, n=1024, buffer=None):
        """ 
        Initialize the object.  If a buffer is specified, use it.
        Otherwise create one.  
        """
        if buffer:
            self._buffer = buffer
            bufSize      = len(buffer)
            if n < bufSize:
                n = bufSize
            elif n > bufSize:
                more = bytearray(n - bufSize)
                self.buffer.extend(more)
        else:
            # allocate and initialize the buffer; init probably a waste of time
            self._buffer    = bytearray(n)

        self._capacity  = n 
        self._limit     = 0         # a change in spec: was = n
        self._position  = 0

    @property
    def buffer(self):   return self._buffer

    @property
    def position(self): return self._position
    @position.setter
    def position(self, offset):
        if offset < 0:
            raise ValueError("position cannot be negative but is '%s'" % offset)
        if (offset >= len(self._buffer)):
            raise ValueError('position cannot be beyond capacity')
        self._position = offset

    @property
    def limit(self):    return self._limit
    @limit.setter
    def limit(self, offset):
        if offset < 0:
            raise ValueError('limit cannot be set to a negative')
        if (offset < self._position):
            raise ValueError("limit can't be set to less than current position")
        if (offset > self._capacity):
            raise ValueError('limit cannot be beyond capacity')
        self._limit = offset

    @property
    def capacity(self): 
        return len(self._buffer)

    def copy(self):
        """ 
        Returns a copy of this Channel using the same underlying
        bytearray.  
        """
        return Channel(len(self._buffer), self._buffer)

    def flip(self):
        self._limit = self._position
        self._position  = 0

    def clear(self):
        self._limit     = 0
        self.position   = 0
