from z3 import *

solver = Solver()

bitstream1 = String('bitstream1')
bitstream2 = String('bitstream2')
offset = Int('offset')

solver.add(bitstream1 == "10001001")
solver.add(SubString(bitstream1, 0, offset) == "1000")
solver.add(SubString(bitstream1, offset, Length(bitstream1)) == "1001")

solver.add(bitstream2 == "11001001")
solver.add(SubString(bitstream2, 0, offset) == "1100")
solver.add(SubString(bitstream2, offset, Length(bitstream2)) == "1001")


print(solver.check())
print(solver.model())
