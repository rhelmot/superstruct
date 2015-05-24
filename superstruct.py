import sys
import struct
from struct import error

__all__ = ('error', 'pack', 'unpack', 'calcsize', 'Struct')

sizes = {'x': 16, 'X': 16, 'y': 32, 'Y': 32, 'z': 64, 'Z': 64}

def unpack(fmt, string):
    return Struct(fmt).unpack(string)

def pack(fmt, *args):
    return Struct(fmt).pack(*args)

def calcsize(fmt):
    return Struct(fmt).size

class Struct(object):
    def __init__(self, fmt, little_endian=None):
        if len(fmt) > 0 and fmt[0] in '@=<>!':
            c = fmt[0]
            fmt = fmt[1:]
            if c in '>!':
                little_endian = False
            elif c == '<':
                little_endian = True
            else:
                little_endian = None

        self.fmt = fmt
        if little_endian is None:
            self.little_endian = sys.byteorder == 'little'
        else:
            self.little_endian = little_endian

        fmt_chr = '<' if self.little_endian else '>'
        partial_fmt = ''
        self._entries = []
        # Entries a list of (is_native, fmt, num_bytes, num_vals)

        for c in self.fmt:
            if c in 'xXyYzZ':
                if partial_fmt != '':
                    num_bytes = struct.calcsize(partial_fmt)
                    num_vals = len(struct.unpack(partial_fmt, '\0'*num_bytes))
                    self._entries.append((True, fmt_chr + partial_fmt, num_bytes, num_vals))
                    partial_fmt = ''
                self._entries.append((False, c, sizes[c], 1))
            elif c == '*':
                partial_fmt += 'x'
            else:
                partial_fmt += c

        if partial_fmt != '':
            num_bytes = struct.calcsize(partial_fmt)
            num_vals = len(struct.unpack(partial_fmt, '\0'*num_bytes))
            self._entries.append((True, fmt_chr + partial_fmt, num_bytes, num_vals))

        self._num_bytes = sum(map(lambda x: x[2], self._entries))
        self._num_vals = sum(map(lambda x: x[3], self._entries))

    @property
    def size(self):
        return self._num_vals

    @property
    def format(self):
        return self.fmt

    def unpack(self, string):
        if len(string) != self._num_bytes:
            raise error('unpack requires a string argument of length %d' % self._num_bytes)

        out = []
        i = 0

        for is_native, fmt, num_bytes, _ in self._entries:
            component = string[i:i+num_bytes]
            i += num_bytes

            if is_native:
                out.extend(struct.unpack(fmt, component))
            else:
                if self.little_endian:
                    component = reversed(component)
                val = 0
                for char in component:
                    val = (val << 8) | ord(char)
                if fmt in 'xyz':
                    if val & (1 << (num_bytes*8 - 1)) != 0:
                        val -= (1 << (num_bytes*8))
                out.append(val)

        return tuple(out)

    def pack(self, *args):
        if len(args) != self._num_vals:
            raise error('pack expected %d items for packing (got %d)' % (self._num_vals, len(args)))

        out = ''
        i = 0

        for is_native, fmt, num_bytes, num_vals in self._entries:
            component = args[i:i+num_vals]
            i += num_vals

            if is_native:
                out += struct.pack(fmt, *component)
            else:
                val = ''
                num = component[0]
                if num < 0:
                    num += (1 << (num_bytes*8))
                for _ in xrange(num_bytes):
                    val += chr(num & 0xFF)
                    num = num >> 8

                if not self.little_endian:
                    val = val[::-1]
                out += val

        return out
