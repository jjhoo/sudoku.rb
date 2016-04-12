require 'rake/testtask'

Rake::TestTask.new(:test) do |test|
  test.libs << 'tests'
  test.pattern = 'tests/tc_sudoku.rb'
  test.verbose = true
end

task :default => :test
