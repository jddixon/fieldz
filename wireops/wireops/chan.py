# ~/dev/py/fieldz/fieldz/chan.py

""" Channel for transmitting and receiving binary data. """

__all__ = ['Channel', ]

# XXX COMPARE WITH Java ByteBuffer

# -- Channel -----------------------------------------------------


class Channel(object):
    """ Channel for transmitting and receiving binary data. """

    __slots__ = ['_buffer', '_capacity', '_limit', '_position', ]

    def __init__(self, nnn=1024, buffer=None):
        """
        Initialize the object.  If a buffer is specified, use it.
        Otherwise create one.
        """
        if buffer:
            self._buffer = buffer
            buf_size = len(buffer)
            if nnn < buf_size:
                nnn = buf_size
            elif nnn > buf_size:
                more = bytearray(nnn - buf_size)
                self.buffer.extend(more)
        else:
            # allocate and initialize the buffer; init probably a waste of time
            self._buffer = bytearray(nnn)

        self._capacity = nnn
        self._limit = 0         # a change in spec: was = n
        self._position = 0

    @property
    def buffer(self):
        """ Return the internal buffer associated with the Channel. """
        return self._buffer

    @property
    def position(self):
        """ Return the current position on the Channel. """
        return self._position

    @position.setter
    def position(self, offset):
        """
        Set the current position on the Channel.

        Raise an exception of the position is out of range.
        """

        if offset < 0:
            raise ValueError(
                "position cannot be negative but is '%s'" %
                offset)
        if offset >= len(self._buffer):
            raise ValueError('position cannot be beyond capacity')
        self._position = offset

    @property
    def limit(self):
        """ Return the current limit on the Channel. """
        return self._limit

    @limit.setter
    def limit(self, offset):
        """ Set the limit on the Channel. """
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
        """ Return the capacity of the Channel, the length of its buffer. """
        return len(self._buffer)

    def copy(self):
        """
        Returns a copy of this Channel using the same underlying
        bytearray.
        """
        return Channel(len(self._buffer), self._buffer)

    def flip(self):
        """
        Flip the channel, making its current position the limit and
        setting its position to zero.
        """
        self._limit = self._position
        self._position = 0

    def clear(self):
        """ Clear the Channel, setting limit and position to zero."""
        self._limit = 0
        self.position = 0
