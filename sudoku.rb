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

UNSOLVED = nil

BOXES = [1, 4, 7] . map { |i| [1, 4, 7] . map { |j| [[i, j], [i+2, j+2]] } } . flatten(1)

def get_box_bounds(box)
  BOXES[box - 1]
end

class Pos
  attr_accessor :row, :column, :box_number

  def initialize(row, col)
    @row = row
    @column = col

    n = (((row - 1) / 3) * 3 + ((column - 1) / 3))
    @box_number = n + 1
  end

  def same_row?(other)
    @row == other.row
  end

  def same_column?(other)
    @column == other.column
  end

  def same_box?(other)
    self.box_number == other.box_number
  end

  def sees?(other)
    self != other and (self.same_row?(other) or
                       self.same_column?(other) or
                       self.same_box?(other))
  end

  def to_s
    "#{@row} #{@column}"
  end

  def ==(other)
    self.class == other.class and
      self.row == other.row and
      self.column == other.column
  end

  def hash
    @row.hash ^ @column.hash
  end

  alias eql? ==
end

class Cell
  attr_accessor :pos, :value
  
  def initialize(pos, value)
    @pos = pos
    @value = value
  end

  def solved?
    @value > 0
  end

  def to_s
    "#{@pos.row} #{@pos.column} #{@value}"
  end

  def ==(other)
    self.class == other.class and
      self.pos == other.pos and
      self.value == other.value
  end

  alias eql? ==
end

class Solver
  attr_accessor :grid, :rows, :columns, :boxes, :candidates
  
  def initialize(str)
    @grid = string_to_grid(str)
    @candidates = []
    self.init
  end

  def init_solved
    @solved = []
    @grid.each do |pos, cell|
      if cell.solved?
        @solved.push Cell.new(cell.pos, cell.value)
      end
    end
  end
  
  def init_unsolved
    @unsolved = []
    @grid.each do |pos, cell|
      if not cell.solved?
        @unsolved.push Cell.new(cell.pos, cell.value)
      end
    end
  end

  def init
    # Remove candidates removable because of initially solved grid
    self.init_solved
    self.init_unsolved

    @candidates = []
    @unsolved.each do |cell|
      (1..9).each do |i|
        candidates.push Cell.new(cell.pos, i)
      end
    end

    @solved.each do |cell|
      # puts "Solved: #{cell}"
      self.update_cell(cell)
    end
  end

  def update_cell(cell)
    candidates.reject! { |cell2| cell.pos == cell2.pos }
    candidates.reject! do |cell2|
      cell.pos != cell2.pos and cell.value == cell2.value and
        (cell.pos.row == cell2.pos.row or
         cell.pos.column == cell2.pos.column or
         cell.pos.box_number == cell2.pos.box_number)
    end
  end

  def dump_candidates
    puts "Candidates"

    coords = @candidates.map { |cell| cell.pos }.uniq
    cells = coords.map { |pos| @candidates.select { |cell| cell.pos == pos} } .
                map { |xs| [xs[0].pos, xs.map { |cell| cell.value }] }
    cells.each do |pos, nums|
      puts "    (#{pos.row}, #{pos.column})    #{nums}"
    end
  end

  def dump_grid
    ios = IO.new(1, "w")
    ios << "Grid" << "\n"

    ios << "     "
    (1..9).each { |i| ios << " " << i }
    ios << "\n\n"

    (1..9).each do |i|
      ios << i << "    "
      (1..9).each do |j|
        cell = @grid[Pos.new(i, j)]
        ios << " " << cell.value
      end
      ios << "\n"
    end
  end

  def solved?
    @candidates.length == 0
  end

  def solve
    puts "Start solving"
    finders = [
      proc {|s| self.find_singles_simple()},
      proc {|s| self.find_singles()},
      proc {|s| self.find_naked_pairs()},
      proc {|s| self.find_naked_triples()},
      proc {|s| self.find_naked_quads()},
      proc {|s| self.find_hidden_pairs()},
      proc {|s| self.find_hidden_triples()},
      proc {|s| self.find_hidden_quads()},
      proc {|s| self.find_pointing_pairs()},
      proc {|s| self.find_boxline_reductions()},
      proc {|s| self.find_xwings()},
      proc {|s| self.find_ywings()},
      proc {|s| self.find_xyzwings()}
    ]
    
    while true
      found = []
      self.dump_candidates

      finders.each do |finder|
        found = finder.call()
        if found.length > 0
          puts "Something found"
          break
        else
          puts "Nothing found"
        end
      end
      if self.solved?
        puts "Solved!"
        self.dump_grid
        break
      end

      if found.length > 0
        next
      end

      puts "No progress"
      self.dump_candidates
      break
    end
  end

  # To be called with solved cells
  def update_grid(found)
    found.each do |x|
      puts "Solved: #{x}"
      cell = @grid[x.pos]
      cell.value = x.value

      @solved.push cell
      @unsolved.reject! { |xx| xx.pos == x.pos }
      self.update_cell(x)
    end
  end

  def update_candidates(found)
    # old = @candidates.dup
    @candidates.reject! { |x| found.include? x }
    #   found.each do |cell|
    #     if not flag
    #       flag = (x.pos == cell.pos and x.value == cell.value)
    #       break
    #     end
    #   end
    #   flag
    # end
    # diff = old - @candidates
    # puts "diff #{diff}"
  end
  
  def get_row (i)
    @candidates.select { |cell| cell.pos.row == i }
  end

  def get_column (i)
    @candidates.select { |cell| cell.pos.column == i }
  end

  def get_box (i)
    @candidates.select { |cell| cell.pos.box_number == i }
  end
  
  def eliminator (fun)
    found = []
    (1..9).each do |i|
      found = found + fun.call(self.get_row(i))
      found = found + fun.call(self.get_column(i))
      found = found + fun.call(self.get_box(i))
    end

    found.uniq! {|x| [x.pos, x.value]}
    found.each do |x|
      puts "eliminator found: #{x}"
    end
    found
  end

  def find_singles_simple
    puts "Find singles simple"
    
    def dummy(set)
      found = []

      # Unique positions
      poss = set.map { |x| x.pos }
      poss.uniq!

      # puts "positions #{poss.length}"
      poss.each do |pos|
        cands = set.select { |x| x.pos == pos }
        # puts "cands #{cands.length}"
        if cands.length == 1
          found.push(cands[0].dup)
        end
      end
      found
    end

    found = eliminator proc { |set| dummy(set) }
    if found.length > 0
      found.each do |x|
        puts "find_singles_simple #{x}"
      end
      self.update_grid(found)
      # self.update_candidates(found)
    end
    found
  end

  def find_singles
    puts "Find singles"
    
    def dummy(set)
      nums = unique_numbers(set)
      found = []

      nums.sort!

      # puts "Numbers #{nums}"
      nums.each do |x|
        nset = set.select { |cell| cell.value == x }
        # puts "nums #{nset.length}"
        if nset.length == 1
          found = found | [ nset[0].dup ]
        end
      end
      found
    end

    found = eliminator proc { |set| dummy(set) }
    if found.length > 0
      found.each do |x|
        puts "find_singles #{x}"
      end

      self.update_grid(found)
      # self.update_candidates(found)
    end
    found
  end

  def find_naked_groups (limit)
    puts "Find naked groups (#{limit})"
    def dummy(set, limit)
      found = []
      nums = unique_numbers(set)
      usable = limit + 1

      return [] if nums.length < usable

      poss = set.map { |x| x.pos }
      poss.uniq!

      # Nothing to be gained
      return [] if poss.length < usable

      cells = poss.map { |pos| [pos,
                                set.select { |cell| cell.pos == pos } .
                                  map { |cell| cell.value }] }

      nums.combination(limit) do |c|
        hits = cells.select do |pos, nums|
          c == nums or (nums - c).length == 0
        end

        if hits.length == limit
          # puts "  triple?? #{c} #{hits} #{set}"
          hits.map! { |pos, nums| pos }
          found = found | set.select do |cell|
            c.include? cell.value and not hits.any? { |pos| pos == cell.pos }
          end
        end
      end
      found
    end

    # tmp = dummy(self.get_box(6))
    # if tmp.length > 0
    #   puts "tmp #{tmp}"
    # end

    found = eliminator proc { |set| dummy(set, limit) }
    if found.length > 0
      found.each do |x|
        puts "find_naked_group(#{limit}) #{x}"
      end

      self.update_candidates(found)
    end
    found
  end

  def find_naked_pairs
    return self.find_naked_groups(2)
  end

  def find_naked_triples
    return self.find_naked_groups(3)
  end

  def find_naked_quads
    return self.find_naked_groups(4)
  end

  def find_hidden_groups(limit)
    puts "Find hidden groups (#{limit})"
    dummy = lambda do |set, limit|
      found = []

      nums = numbers(set)
      ncts = number_counts(nums, limit)
      unums = ncts.map { |a, _cnt| a }

      usable = limit + 1
      return [] if unums.length < usable

      poss = set.map(&:pos)
      poss.uniq!

      # Nothing to be gained
      return [] if poss.length < usable

      cells = poss.map do |pos|
        [pos, set.select { |cell| cell.pos == pos }.map(&:value)]
      end

      # puts "  pair? #{ncts} #{unums}"
      unums.combination(limit) do |c|
        hits = cells.select do |_pos, nums|
          (c & nums).length == limit
        end
        next unless hits.length == limit

        # puts "  pair???? #{c} #{hits}"

        if hits.length == limit
          found |= set.select do |cell|
            not c.include? cell.value and
              hits.any? { |pos, _nums| pos == cell.pos }
          end
        end
      end
      found
    end

    # tmp = dummy(get_box(6))
    # if tmp.length > 0
    #   puts "tmp #{tmp}"
    # end

    found = eliminator proc { |set| dummy.call(set, limit) }
    if found.length > 0
      found.each do |x|
        puts "find_hidden_group(#{limit}) #{x}"
      end

      update_candidates(found)
    end
    found
  end

  def find_hidden_pairs
    find_hidden_groups(2)
  end

  def find_hidden_triples
    find_hidden_groups(3)
  end

  def find_hidden_quads
    find_hidden_groups(4)
  end

  def find_pointing_pairs
    puts "Find pointing pairs"
    def dummy(set, psameline)
      return [] if set.length < 3
      nums = unique_numbers(set)

      return [] if nums.length < 3

      found = []

      nums.each do |x|
        nset = set.select { |cell| cell.value == x }
        if nset.length > 2
          nset.each do |a|
            nset.each do |b|
              next if a.pos == b.pos

              if a.pos.box_number == b.pos.box_number and
                psameline.call(a, b)

                # puts "Maybe a pointing pair #{a}, #{b}"

                bset = self.get_box(a.pos.box_number)
                bset.select! { |cell| cell.value == x }

                if bset.length == 2
                  # puts "   pointing pair #{a}, #{b}"

                  found = found | nset.reject do |cell|
                    cell.pos == a.pos or cell.pos == b.pos
                  end
                end
              end
            end
          end
        end
      end
      found
    end

    found = []
    (1..9).each do |i|
      set = self.get_row(i)
      found = found | dummy(set, proc { |a, b| a.pos.row == b.pos.row })
    end

    (1..9).each do |i|
      set = self.get_column(i)
      found = found | dummy(set, proc { |a, b| a.pos.column == b.pos.column })
    end

    if found.length > 0
      found.each do |x|
        puts "find_pointing_pairs #{x}"
      end
      self.update_candidates(found)
    end
    found
  end

  def find_xwings
    puts "Find x-wings"
    def dummy(pgetset, pother, ppos, pposother)
      found = []
      (1..8).each do |i|
        j0 = i + 1

        aset = pgetset.call(i)
        anums = numbers(aset)

        as = number_counts(anums, 2)
        next if as.length == 0

        (j0..9).each do |j|
          bset = pgetset.call(j)

          bnums = numbers(bset)
          bs = number_counts(bnums, 2)
          next if bs.length == 0
          # puts "xwing? #{i} #{j} #{as} #{bs}"

          as.each do |a, _|
            bs.each do |b, _|
              next if a != b
              # puts "xwing?? #{i} #{j} #{a} #{b}"
              apos = aset.select { |cell| cell.value == a } .
                     map { |cell| ppos.call(cell.pos) }
              bpos = bset.select { |cell| cell.value == b } .
                     map { |cell| ppos.call(cell.pos) }

              if apos.length == 2 and apos == bpos
                # puts "xwing??? #{i} #{j} #{a} #{b} #{apos} #{bpos}"
                found = pother.call(apos[0]) .
                        select { |cell| cell.value == a and
                                 pposother.call(cell.pos) != i and
                                 pposother.call(cell.pos) != j }
                found += pother.call(apos[1]) .
                        select { |cell| cell.value == a and
                                 pposother.call(cell.pos) != i and
                                 pposother.call(cell.pos) != j }
              end
            end
          end
        end
      end
      found
    end

    found = dummy(proc { |i| self.get_row(i) },
                  proc { |i| self.get_column(i) },
                  proc { |pos| pos.column },
                  proc { |pos| pos.row })
    found = found | dummy(proc { |i| self.get_column(i) },
                          proc { |i| self.get_row(i) },
                          proc { |pos| pos.row },
                          proc { |pos| pos.column })

    if found.length > 0
      found.each do |x|
        puts "find_xwings #{x}"
      end
      self.update_candidates(found)
    end
    found
  end

  def find_xyzwings
    puts "Find xyz-wings"
    found = []

    # Need to get cells that have 2 or 3 numbers
    coords = @candidates.map { |cell| cell.pos }.uniq
    cells = coords.map { |pos| @candidates.select { |cell| cell.pos == pos} } .
            select { |foo| foo.length == 2 or foo.length == 3 } .
            map { |xs| [xs[0].pos, xs.map { |cell| cell.value }] }
    cells.each do |a, anums|
      next unless anums.length == 2

      cells.each do |b, bnums|
        next if a == b
        next if a.row < b.row
        next unless bnums.length == 2

        cells.each do |w, wnums|
          next if a == w or b == w
          next unless wnums.length == 3
          next unless wnums == (anums | bnums).sort
          next unless w.sees?(a) and w.sees?(b)

          # puts "consider #{a} - #{b} - #{w}"
          # puts "	     #{anums} - #{bnums} - #{wnums}"

          z = (anums & bnums)[0]
          found = found | @candidates.select { |cell| cell.value == z and
                                               a.sees?(cell.pos) and
                                               b.sees?(cell.pos) and
                                               w.sees?(cell.pos) } .
                          uniq {|cell| cell.pos}
        end
      end
    end

    if found.length > 0
      found.each do |x|
        puts "find_xyzwings #{x}"
      end
      self.update_candidates(found)
    end
    found
  end

  def find_ywings
    puts "Find y-wings"
    found = []

    # Need to get cells that have 2
    coords = @candidates.map { |cell| cell.pos }.uniq
    cells = coords.map { |pos| @candidates.select { |cell| cell.pos == pos} } .
            select { |foo| foo.length == 2 } .
            map { |xs| [xs[0].pos, xs.map { |cell| cell.value }] }

    cells.each do |a, anums|
      cells.each do |b, bnums|
        next if a == b

        cells.each do |hinge, hnums|
          next if a == hinge or b == hinge

          next if anums == bnums
          next if anums == hnums
          tmp = anums & bnums
          next unless tmp.length == 1
          z = tmp[0]

          next unless hnums == (anums | bnums).sort - tmp
          next unless hinge.sees?(a) and hinge.sees?(b)

          # puts "consider #{a} - #{b} - #{hinge}"
          # puts "	     #{anums} - #{bnums} - #{hnums}"

          found = found | @candidates.select { |cell| cell.value == z and
                                               a.sees?(cell.pos) and
                                               b.sees?(cell.pos) } .
                          uniq {|cell| cell.pos}
        end
      end
    end

    if found.length > 0
      found.each do |x|
        puts "find_ywings #{x}"
      end
      self.update_candidates(found)
    end
    found
  end

  def find_boxline_reductions
    puts "Find box/line reductions"
    found = []

    def dummy(box)
      found = []

      set = self.get_box(box)
      return [] if set.length <= 2

      ulc, lrc = get_box_bounds(box)

      (ulc[0]..lrc[0]).each do |i|
        next if set.select { |cell| cell.pos.row == i } . length < 2
        row = self.get_row(i)
        nums = numbers(row)

        # row has two possible cells for N, and they are in the box?
        foos = number_counts(nums, 2)
        next if foos.length == 2

        foos.each do |x, cnt|
          cells = row.select { |cell| cell.value == x and
                               cell.pos.box_number == box}
          next unless cells.length == 2
          found = found | set.select { |cell| cell.value == x and
                                       cell.pos.row != i }
          # puts "box #{i} #{box} #{ulc} #{lrc} #{x} #{cnt} #{found.length}"
        end
      end

      (ulc[1]..lrc[1]).each do |i|
        next if set.select { |cell| cell.pos.column == i } . length < 2
        column = self.get_column(i)
        nums = numbers(column)

        # row has two possible cells for N, and they are in the box?
        foos = number_counts(nums, 2)
        next if foos.length == 2

        foos.each do |x, cnt|
          cells = column.select { |cell| cell.value == x and
                                  cell.pos.box_number == box}
          next unless cells.length == 2
          found = found | set.select { |cell| cell.value == x and
                                       cell.pos.column != i }
          # puts "box #{i} #{box} #{ulc} #{lrc} #{x} #{cnt} #{found.length}"
        end
      end
      found
    end

    (1..9).each do |i|
      found = found | dummy(i)
    end

    if found.length > 0
      found.each do |x|
        puts "find_boxline_reductions #{x}"
      end
      self.update_candidates(found)
    end
    found
  end
end

def numbers(set)
  nums = []
  set.each { |cell| nums = nums + [cell.value] }
  nums.sort!
  nums
end

def unique_numbers(set)
  nums = []
  set.each { |cell| nums = nums | [cell.value] }
  nums.sort!
  nums
end

def number_counts(numbers, target=nil)
  res = []
  numbers.each do |a|
    res.push [a, (numbers.select { |b| b == a }).length]
  end
  if target != nil
    res.select! { |a, b| b == target }
  end
  res.uniq!
  res
end

def string_to_grid(str)
  i = 1
  j = 1
  grid = Hash.new
  
  str.each_char do |c|
    val = Integer(c)
    pos = Pos.new(i, j)
    cell = Cell.new(pos, val)
    grid[pos] = cell
    
    j += 1
    if (j % 10) == 0
      i += 1
      j = 1
    end
  end
  grid
end

# needs naked triple, y-wing
# GRID = "014600300050000007090840100000400800600050009007009000008016030300000010009008570"
#
# can proceed with box/line reduction
GRID = "200068050008002000560004801000000530400000002097000000804300096000800300030490007"

if GRID.length != 81
  puts "Bad input"
  exit
end

puts GRID
solver = Solver.new GRID
solver.solve

# strategies = [ ["singles", eliminateSingles],
#                ["naked pairs", eliminatePairs],
#                ["naked triples", eliminateTriples],
#                ["naked quads", eliminateQuads],
#                ["pointing pairs", eliminatePointingPairs],
#                ["box line reduction", eliminateBoxLineReduction],
#                ["X-wing", eliminateXWings],
#                ["Y-wing", eliminateYWings],
#                ["XYZ-wing", eliminateXYZWings]]
# puts solved
# solved.each
# puts candidates
