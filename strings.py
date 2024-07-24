from z3 import *

solver = Solver()

bitstream = String('bitstream')
offset = Int('offset')

solver.add(bitstream == "10001001")
solver.add(SubString(bitstream, 0, offset) == "1000")
solver.add(SubString(bitstream, offset, Length(bitstream)) == "1001")

print(solver.check())
print(solver.model())
