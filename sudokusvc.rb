# coding: iso-8859-1
#
# Copyright (c) 2015 Jani J. Hakala <jjhakala@gmail.com> Jyväskylä, Finland
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
require 'bert'
require 'bert/decoder'
require 'fileutils'
require 'securerandom'
require 'socket'
require 'pp'

require_relative 'sudoku'

user = ENV['USER']

class Connection
  attr_accessor :handler

  def initialize(socket)
    @socket = socket
    @handler = nil
  end

  def read_msg_length
    begin
      data = @socket.recv_nonblock 4
      fail IOError, 'Connection closed' if data.empty?
      berp_len = data.unpack('N')[0]
    rescue Errno::EAGAIN
      IO.select([@socket], [], [], 1.0)
      retry
    end
    berp_len
  end

  def read_msg(length)
    left = length
    berp_msg = ''

    while left > 0 do
      begin
        data = @socket.recv_nonblock left
        if data.empty?
          raise IOError, "Connection closed"
        end
        berp_msg << data
        left -= data.length
      rescue Errno::EAGAIN
        IO.select([@socket], [], [], 1.0)
        retry
      end
    end
    berp_msg
  end

  def run_it
    loop do
      berp_len = read_msg_length
      berp_msg = read_msg(berp_len)

      # puts "BERP Massage ends at #{Time.now} |#{berp_msg}| #{berp_msg[0]} #{berp_msg[1]}"
      msg = BERT::Decoder.decode(berp_msg)
      fail TypeError, 'Unexpected type' unless msg.instance_of? BERT::Tuple

      # puts "BERT #{msg}"
      case msg[0]
      when :info
        @handler.handle_info(msg[1], msg[2])
      when :call
        @handler.handle_call(msg[1], msg[2], msg[3])
      when :cast
        @handler.handle_cast(msg[1], msg[2], msg[3])
      when :error
        @handler.handle_error(msg)
      end
    end
  end

  def sendall(msg)
    sent = 0

    while sent < msg.length
      slice = msg.slice(sent, 4096)
      # puts "Send slice #{slice} #{slice.length}"
      count = @socket.send slice, 0
      # puts "Sent slice #{slice} #{slice.length} #{count}"
      fail IOError, 'Connection closed' if count == 0
      sent += count

      # puts "Send #{sent} #{msg.length}"
    end
    # puts "Send complete"
  end

  def send_reply(term)
    bin = BERT::Encoder.encode(term)
    msg = [bin.length].pack('N') + bin
    # puts "BERT reply #{term} #{msg.length}"
    # bin.each_char { |c| printf '%02x ', c.ord }
    # print "\n"
    sendall msg
  end
end

class Handler
  def initialize(connection)
    @connection = connection
    @info_cmd = nil
    @info_opts = nil
  end

  def handle_call(m, f, a)
    # puts "BERT call #{m} #{f} #{a}"
    send(f, *a)
  end

  def handle_info(command, options)
    # puts "BERT info #{command} #{options}"
    @info_cmd = command
    @info_opts = options
  end

  def handle_cast(m, f, a)
    # puts "BERT cast #{m} #{f} #{a}"
    self.send("cast_#{f}".to_sym, *a)
  end

  def handle_error(m, f, a)
    puts "BERT error #{msg}"
  end

  def reply_ok
    @connection.send_reply(t[:reply, :ok])
  end

  def reply(term)
    @connection.send_reply(t[:reply, term])
  end
end

class Sudoku_Handler < Handler
  def initialize(socket)
    super socket
  end

  def init(grid)
    puts "Sudoku init #{grid}"
    @grid = grid
    reply_ok
  end

  def solve
    puts "Sudoku solve"
    solver = Solver.new @grid
    unless solver.valid?
      reply(:invalid_grid)
      return
    end
    solver.solve
    status = (solver.solved? and solver.valid?) ? :solved : :unsolved
    reply(t[status, solver.to_s])
  end
end

# server = TCPServer.new 2000
begin
  if File.stat("/tmp/sudokusocket-#{user}").directory?
    FileUtils.chmod 0700, "/tmp/sudokusocket-#{user}"
  end
rescue Errno::ENOENT
  FileUtils.mkdir "/tmp/sudokusocket-#{user}", mode: 0700
end

begin
  if File.stat("/tmp/sudokusocket-#{user}/sudoku.sock").socket?
    FileUtils.rm "/tmp/sudokusocket-#{user}/sudoku.sock"
  end
rescue Errno::ENOENT
  true
end

#
# server = TCPServer.new 'localhost', 7777
server = UNIXServer.new "/tmp/sudokusocket-#{user}/sudoku.sock"
loop do
  Thread.start(server.accept) do |client_sock|
    begin
      conn = Connection.new client_sock
      handler = Sudoku_Handler.new conn
      conn.handler = handler
      conn.run_it
    rescue
      pp $ERROR_INFO
    end
  end
end

# module SudokuSvc
#   class State
#     def initialize(grid)
#       @grid = grid
#     end
#   end

#   class SudokuSvc
#     def initialize
#       @sessions = {}
#     end

#     def init(grid)
#       key = SecureRandom.base64
#       @sessions[key] = State.new grid
#       return grid
#     end
#   end
# end
