# Copyright (c) 2009-2013 Samuel Stauffer <samuel@descolada.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# 3. Neither the name of Samuel Stauffer nor the names of its contributors
#	 may be used to endorse or promote products derived from this software
#	 without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import division

import struct
import zlib
import six

from erlastic.constants import *
from erlastic.types import *

__all__ = ["ErlangTermEncoder", "ErlangTermDecoder", "EncodingError"]

class EncodingError(Exception):
    pass

class ErlangTermDecoder(object):
    def __init__(self):
        # Cache decode functions to avoid having to do a getattr
        self.decoders = {}
        for k in self.__class__.__dict__:
            v = getattr(self, k)
            if callable(v) and k.startswith('decode_'):
                try: self.decoders[int(k.split('_')[1])] = v
                except: pass

    def decode(self, buf, offset=0):
        if six.PY2 and isinstance(buf, basestring):
            buf = bytearray(buf)
        version = buf[offset]
        if version != FORMAT_VERSION:
            raise EncodingError("Bad version number. Expected %d found %d" % (FORMAT_VERSION, version))
        return self.decode_part(buf, offset+1)[0]

    def decode_part(self, buf, offset=0):
        return self.decoders[buf[offset]](buf, offset+1)

    def decode_97(self, buf, offset):
        """SMALL_INTEGER_EXT"""
        return buf[offset], offset+1

    def decode_98(self, buf, offset):
        """INTEGER_EXT"""
        return struct.unpack(">l", buf[offset:offset+4])[0], offset+4

    def decode_99(self, buf, offset):
        """FLOAT_EXT"""
        return float(buf[offset:offset+31].split(b'\x00', 1)[0]), offset+31

    def decode_70(self, buf, offset):
        """NEW_FLOAT_EXT"""
        return struct.unpack(">d", buf[offset:offset+8])[0], offset+8

    def decode_100(self, buf, offset):
        """ATOM_EXT"""
        atom_len = struct.unpack(">H", buf[offset:offset+2])[0]
        atom = buf[offset+2:offset+2+atom_len]
        return self.convert_atom(atom), offset+atom_len+2

    def decode_115(self, buf, offset):
        """SMALL_ATOM_EXT"""
        atom_len = buf[offset]
        atom = buf[offset+1:offset+1+atom_len]
        return self.convert_atom(atom), offset+atom_len+1

    def decode_104(self, buf, offset):
        """SMALL_TUPLE_EXT"""
        arity = buf[offset]
        offset += 1

        items = []
        for i in range(arity):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        return tuple(items), offset

    def decode_105(self, buf, offset):
        """LARGE_TUPLE_EXT"""
        arity = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4

        items = []
        for i in range(arity):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        return tuple(items), offset

    def decode_106(self, buf, offset):
        """NIL_EXT"""
        return [], offset

    def decode_107(self, buf, offset):
        """STRING_EXT"""
        length = struct.unpack(">H", buf[offset:offset+2])[0]
        st = buf[offset+2:offset+2+length]
        return st, offset+2+length

    def decode_108(self, buf, offset):
        """LIST_EXT"""
        length = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4
        items = []
        for i in range(length):
            val, offset = self.decode_part(buf, offset)
            items.append(val)
        tail, offset = self.decode_part(buf, offset)
        if tail != []:
            # TODO: Not sure what to do with the tail
            raise NotImplementedError("Lists with non empty tails are not supported")
        return items, offset

    def decode_109(self, buf, offset):
        """BINARY_EXT"""
        length = struct.unpack(">L", buf[offset:offset+4])[0]
        return buf[offset+4:offset+4+length], offset+4+length

    def decode_110(self, buf, offset):
        """SMALL_BIG_EXT"""
        n = buf[offset]
        offset += 1
        return self.decode_bigint(n, buf, offset)

    def decode_111(self, buf, offset):
        """LARGE_BIG_EXT"""
        n = struct.unpack(">L", buf[offset:offset+4])[0]
        offset += 4
        return self.decode_bigint(n, buf, offset)

    def decode_bigint(self, n, buf, offset):
        sign = buf[offset]
        offset += 1
        b = 1
        val = 0
        for i in range(n):
            val += buf[offset] * b
            b <<= 8
            offset += 1
        if sign != 0:
            val = -val
        return val, offset

    def decode_101(self, buf, offset):
        """REFERENCE_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing REFERENCE_EXT, found %r instead" % node)
        reference_id, creation = struct.unpack(">LB", buf[offset:offset+5])
        return Reference(node, [reference_id], creation), offset+5

    def decode_114(self, buf, offset):
        """NEW_REFERENCE_EXT"""
        id_len = struct.unpack(">H", buf[offset:offset+2])[0]
        node, offset = self.decode_part(buf, offset+2)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing NEW_REFERENCE_EXT, found %r instead" % node)
        creation = buf[offset]
        reference_id = struct.unpack(">%dL" % id_len, buf[offset+1:offset+1+4*id_len])
        return Reference(node, reference_id, creation), offset+1+4*id_len

    def decode_102(self, buf, offset):
        """PORT_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PORT_EXT, found %r instead" % node)
        port_id, creation = struct.unpack(">LB", buf[offset:offset+5])
        return Port(node, port_id, creation), offset+5

    def decode_103(self, buf, offset):
        """PID_EXT"""
        node, offset = self.decode_part(buf, offset)
        if not isinstance(node, Atom):
            raise EncodingError("Expected atom while parsing PID_EXT, found %r instead" % node)
        pid_id, serial, creation = struct.unpack(">LLB", buf[offset:offset+9])
        return PID(node, pid_id, serial, creation), offset+9

    def decode_113(self, buf, offset):
        """EXPORT_EXT"""
        module, offset = self.decode_part(buf, offset)
        if not isinstance(module, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % module)
        function, offset = self.decode_part(buf, offset)
        if not isinstance(function, Atom):
            raise EncodingError("Expected atom while parsing EXPORT_EXT, found %r instead" % function)
        arity, offset = self.decode_part(buf, offset)
        if not isinstance(arity, int):
            raise EncodingError("Expected integer while parsing EXPORT_EXT, found %r instead" % arity)
        return Export(module, function, arity), offset+1

    def decode_80(self, buf, offset):
        """Compressed term"""
        usize = struct.unpack(">L", buf[offset:offset+4])[0]
        buf = zlib.decompress(buf[offset+4:offset+4+usize])
        return self.decode_part(buf, 0)

    def convert_atom(self, atom):
        if atom == b"true":
            return True
        elif atom == b"false":
            return False
        elif atom == b"none":
            return None
        return Atom(atom.decode('latin-1'))

class ErlangTermEncoder(object):
    def __init__(self, encoding="utf-8", unicode_type="binary"):
        self.encoding = encoding
        self.unicode_type = unicode_type

    def encode(self, obj, compressed=False):
        # import sys
        # import pprint
        # pprint.pprint(self.encode_part(obj),stream=sys.stderr)
        ubuf = b"".join(self.encode_part(obj))
        if compressed is True:
            compressed = 6
        if not (compressed is False \
                    or (isinstance(compressed, int) \
                            and compressed >= 0 and compressed <= 9)):
            raise TypeError("compressed must be True, False or "
                            "an integer between 0 and 9")
        if compressed:
            cbuf = zlib.compress(ubuf, compressed)
            if len(cbuf) < len(ubuf):
                usize = struct.pack(">L", len(ubuf))
                ubuf = "".join([COMPRESSED, usize, cbuf])
        return struct.pack("B", FORMAT_VERSION) + ubuf

    def encode_part(self, obj):
        if obj is False:
            return [struct.pack(">BH", ATOM_EXT, 5) + b"false"]
        elif obj is True:
            return [struct.pack(">BH", ATOM_EXT, 4) + b"true"]
        elif obj is None:
            return [struct.pack(">BH", ATOM_EXT, 4) + b"none"]
        elif isinstance(obj, int):
            if 0 <= obj <= 255:
                return [struct.pack(">BB", SMALL_INTEGER_EXT, obj)]
            elif -2147483648 <= obj <= 2147483647:
                return [struct.pack(">Bl", INTEGER_EXT, obj)]
            else:
                sign = obj < 0
                obj = abs(obj)

                big_buf = []
                while obj > 0:
                    big_buf.append(obj & 0xff)
                    obj >>= 8

                if len(big_buf) < 256:
                    return [struct.pack(">BBB", SMALL_BIG_EXT, len(big_buf), sign), big_buf]
                else:
                    return [struct.pack(">BLB", LARGE_BIG_EXT, len(big_buf), sign), big_buf]
        elif isinstance(obj, float):
            floatstr = ("%.20e" % obj).encode('ascii')
            return [struct.pack(">B", FLOAT_EXT), floatstr, b"\x00"*(31-len(floatstr))]
        elif isinstance(obj, Atom):
            st = obj.encode('latin-1')
            return [struct.pack(">BH", ATOM_EXT, len(st)), st]
        elif isinstance(obj, str):
            st = obj.encode('utf-8')
            return [struct.pack(">BL", BINARY_EXT, len(st)), st]
        elif isinstance(obj, bytes):
            return [struct.pack(">BL", BINARY_EXT, len(obj)), obj]
        elif isinstance(obj, tuple):
            n = len(obj)
            if n < 256:
                buf = [struct.pack('BB', SMALL_TUPLE_EXT, n)]
            else:
                buf = [struct.pack('>BL', LARGE_TUPLE_EXT, n)]
            for item in obj:
                buf += self.encode_part(item)
            return buf
        elif obj == []:
            return [struct.pack(">B", NIL_EXT)]
        elif isinstance(obj, list):
            buf = [struct.pack(">BL", LIST_EXT, len(obj))]
            for item in obj:
                buf += self.encode_part(item)
            buf.append(struct.pack(">B", NIL_EXT)) # list tail - no such thing in Python
            return buf
        elif isinstance(obj, Reference):
            return [
                struct.pack(">BHBH", NEW_REFERENCE_EXT, len(obj.ref_id),
                            ATOM_EXT, len(obj.node)), obj.node.encode('latin-1'),
                struct.pack("B", obj.creation),
                struct.pack(">%dL" % len(obj.ref_id), *obj.ref_id)]
        elif isinstance(obj, Port):
            return [
                struct.pack(">BBH", PORT_EXT, ATOM_EXT, len(obj.node)),
                obj.node.encode('latin-1'), struct.pack(">LB", obj.port_id, obj.creation)]
        elif isinstance(obj, PID):
           return [
                struct.pack(">BBH", PID, ATOM_EXT, len(obj.node)), obj.node.encode('latin-1'),
                struct.pack(">LLB", obj.pid_id, obj.serial, obj.creation)]
        elif isinstance(obj, Export):
            return [
                struct.pack(">BBH", EXPORT_EXT, ATOM_EXT, len(obj.module)), obj.module.encode('latin-1'),
                struct.pack(">BH", ATOM_EXT, len(obj.function)), obj.function.encode('latin-1'),
                struct.pack(">BB", SMALL_INTEGER_EXT, obj.arity)]
        else:
            raise NotImplementedError("Unable to serialize %r" % obj)
