#/usr/bin/python
# coding: latin1
#
# Copyright (c) 2016 Jani J. Hakala <jjhakala@gmail.com> Jyväskylä, Finland
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, version 3 of the
#  License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import socket
import struct
import sys

from erlastic import ErlangTermDecoder, ErlangTermEncoder, Atom

def is_ok_reply(reply):
    return len(reply) == 2 and reply[0] == 'reply' and reply[1] == 'ok'

class Connection(object):
    def __init__(self, socket):
        self.socket = socket
        self.decoder = ErlangTermDecoder()
        self.encoder = ErlangTermEncoder()

    def send_packet4(self, msg):
        msg = struct.pack('>L', len(msg)) + msg
        berp_len = 4 + len(msg)
        self.socket.sendall(msg)

    def recv_packet4(self):
        # print 'recv_packet4 0'
        data = self.socket.recv(4)
        if data == '': raise IOError('Connection closed')

        # print 'recv_packet4 1', data
        msg_size, = struct.unpack('>L', data)
        if msg_size == 0: return None

        # print 'recv_packet4 2', msg_size
        msg = []
        received = 0
        while received < msg_size:
            left = msg_size - received
            if left > 4096:
                data = self.socket.recv(4096)
            else:
                data = self.socket.recv(left)

            if len(data) == 0: raise IOError('Connection closed')
            msg.append(data)
            received += len(data)
        msg = b''.join(msg)
        # print 'recv_packet4 3', repr(msg), ord(msg[0])
        return (msg_size, msg)

    def call(self, module, function, args):
        msg = self.encoder.encode((Atom('call'), Atom(module), Atom(function), args))
        print "Send ", repr(msg)
        self.send_packet4(msg)
        size, data = self.recv_packet4()
        msg = self.decoder.decode(data)
        return msg

    def cast(self, module, function, args):
        msg = self.encoder.encode((Atom('cast'), Atom(module), Atom(function), args))
        self.send_packet4(msg)

    def info(self, command, options):
        msg = self.encoder.encode((Atom('info'), Atom(command), options))
        self.send_packet4(msg)

def connect_unix(path):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(path)
    return s

# user = os.getenv('USER')
# sock = connect_unix('/tmp/sudokusocket-' + user + os.sep + 'sudoku.sock')
# conn = Connection(sock)

# conn.call('sudoku', 'init', '610320000300400000058600000009503620000040000023801500000006750000004003000058014')
# time.sleep(5)
