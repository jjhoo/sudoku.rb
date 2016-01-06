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

__all__ = ['Atom', 'Reference', 'Port', 'PID', 'Export']

class Atom(str):
    def __repr__(self):
        return "Atom(%s)" % super(Atom, self).__repr__()

class Reference(object):
    def __init__(self, node, ref_id, creation):
        if not isinstance(ref_id, tuple):
            ref_id = tuple(ref_id)
        self.node = node
        self.ref_id = ref_id
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, Reference) and self.node == other.node and self.ref_id == other.ref_id and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Ref<%d.%s>" % (self.creation, ".".join(str(i) for i in self.ref_id))

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class Port(object):
    def __init__(self, node, port_id, creation):
        self.node = node
        self.port_id = port_id
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, Port) and self.node == other.node and self.port_id == other.port_id and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Port<%d.%d>" % (self.creation, self.port_id)

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class PID(object):
    def __init__(self, node, pid_id, serial, creation):
        self.node = node
        self.pid_id = pid_id
        self.serial = serial
        self.creation = creation

    def __eq__(self, other):
        return isinstance(other, PID) and self.node == other.node and self.pid_id == other.pid_id and self.serial == other.serial and self.creation == other.creation
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "<%d.%d.%d>" % (self.creation, self.pid_id, self.serial)

    def __repr__(self):
        return "%s::%s" % (self.__str__(), self.node)

class Export(object):
    def __init__(self, module, function, arity):
        self.module = module
        self.function = function
        self.arity = arity

    def __eq__(self, other):
        return isinstance(other, Export) and self.module == other.module and self.function == other.function and self.arity == other.arity
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "#Fun<%s.%s.%d>" % (self.module, self.function, self.arity)

    def __repr__(self):
        return self.__str__()
