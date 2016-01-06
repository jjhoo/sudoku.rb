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

FORMAT_VERSION = 131

NEW_FLOAT_EXT = 70      # [Float64:IEEE float]
BIT_BINARY_EXT = 77     # [UInt32:Len, UInt8:Bits, Len:Data]
SMALL_INTEGER_EXT = 97  # [UInt8:Int]
INTEGER_EXT = 98        # [Int32:Int]
FLOAT_EXT = 99          # [31:Float String] Float in string format (formatted "%.20e", sscanf "%lf"). Superseded by NEW_FLOAT_EXT
ATOM_EXT = 100          # 100 [UInt16:Len, Len:AtomName] max Len is 255
REFERENCE_EXT = 101     # 101 [atom:Node, UInt32:ID, UInt8:Creation]
PORT_EXT = 102          # [atom:Node, UInt32:ID, UInt8:Creation]
PID_EXT = 103           # [atom:Node, UInt32:ID, UInt32:Serial, UInt8:Creation]
SMALL_TUPLE_EXT = 104   # [UInt8:Arity, N:Elements]
LARGE_TUPLE_EXT = 105   # [UInt32:Arity, N:Elements]
NIL_EXT = 106           # empty list
STRING_EXT = 107        # [UInt32:Len, Len:Characters]
LIST_EXT = 108          # [UInt32:Len, Elements, Tail]
BINARY_EXT = 109        # [UInt32:Len, Len:Data]
SMALL_BIG_EXT = 110     # [UInt8:n, UInt8:Sign, n:nums]
LARGE_BIG_EXT = 111     # [UInt32:n, UInt8:Sign, n:nums]
NEW_FUN_EXT = 112       # [UInt32:Size, UInt8:Arity, 16*Uint6-MD5:Uniq, UInt32:Index, UInt32:NumFree, atom:Module, int:OldIndex, int:OldUniq, pid:Pid, NunFree*ext:FreeVars]
EXPORT_EXT = 113        # [atom:Module, atom:Function, smallint:Arity]
NEW_REFERENCE_EXT = 114 # [UInt16:Len, atom:Node, UInt8:Creation, Len*UInt32:ID]
SMALL_ATOM_EXT = 115    # [UInt8:Len, Len:AtomName]
FUN_EXT = 117           # [UInt4:NumFree, pid:Pid, atom:Module, int:Index, int:Uniq, NumFree*ext:FreeVars]
COMPRESSED = 80         # [UInt4:UncompressedSize, N:ZlibCompressedData]
