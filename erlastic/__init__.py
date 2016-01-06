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

"""Erlang External Term Format serializer/deserializer"""

__version__ = "2.0.0"
__license__ = "BSD"

from erlastic.codec import ErlangTermDecoder, ErlangTermEncoder
from erlastic.types import *

encode = ErlangTermEncoder().encode
decode = ErlangTermDecoder().decode

import struct
import sys
def mailbox_gen():
  while True:
    len_bin = sys.stdin.buffer.read(4)
    if len(len_bin) != 4:
      yield None
    (length,) = struct.unpack('!I',len_bin)
    yield decode(sys.stdin.buffer.read(length))
def port_gen():
  while True:
    term = encode((yield))
    sys.stdout.buffer.write(struct.pack('!I',len(term)))
    sys.stdout.buffer.write(term)
def port_connection():
  port = port_gen()
  next(port)
  return mailbox_gen(),port
