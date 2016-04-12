require 'helper'

require "sudoku"
require "test/unit"

def test_grid(grid)
  solver = Solver.new grid
  return false unless solver.valid?
  solver.solve
  solver.solved? and solver.valid?
end

class TestSudoku < Test::Unit::TestCase
  def test_simple
    tst = lambda do |grid|
      solver = Solver.new grid
      return false unless solver.valid?
      solver.solve
      solver.solved? and solver.valid?
    end

    assert(tst.call('510320000300400000058600000009503620000040000023801500000006750000004003000058014') == false)
  end

  def test_hidden_pair
    assert(test_grid('000000000904607000076804100309701080008000300050308702007502610000403208000000000'))
  end

  def test_hidden_triple
    assert(test_grid('300000000970010000600583000200000900500621003008000005000435002000090056000000001'))
  end

  def test_nakedtriple_pointingpairs_ywing
    assert(test_grid('014600300050000007090840100000400800600050009007009000008016030300000010009008570'))
  end

  def test_boxline_reduction
    assert(test_grid('200068050008002000560004801000000530400000002097000000804300096000800300030490007'))
  end

  def test_xyzwing
    assert(test_grid('100002000050090204000006700034001005500908007800400320009600000306010040000700009'))
  end
end
