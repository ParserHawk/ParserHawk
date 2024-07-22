from z3 import *

s = Solver()
seq = Const('seq', SeqSort(IntSort()))
s.add(Length(seq) >= 5)
x = Int('x')
print(SubSeq(seq, 0, x))
