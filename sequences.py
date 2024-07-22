# use z3 -in to use z3 as a REPL

from z3 import *

s = Solver()
seq = Const('seq', SeqSort(IntSort()))
s.add(Length(seq) >= 5)
s.add(seq.at(0) == Unit(Int(1)))
s.add(seq.at(1) == Unit(Int(1)))
s.add(seq.at(2) == Unit(Int(1)))
s.add(seq.at(3) == Unit(Int(1)))
s.add(seq.at(4) == Unit(Int(1)))
#x = Int('x')
#print(SubSeq(seq, 0, x))
s.check()
print(s.model())
