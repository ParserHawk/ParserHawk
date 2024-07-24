from z3 import *

### parse differently depending on the value of the 4th bit from left
### uses three states: first has an extract and select. second has a single extract. third has two extracts.
### 10001001 -> ['1000', '1001']
### 11001001 -> ['1100', '10', '01']

solver = Solver()

bitstream1 = String('bitstream1')
bitstream2 = String('bitstream2')
pred_location = Int('pred_location')
pred_value = String('pred_value') 
offset1 = Int('offset1')
offset2 = Int('offset2')
offset3 = Int('offset3')

solver.add(bitstream1 == "10001001")
solver.add(SubString(bitstream1, 0, offset1) == "1000")
solver.add(SubString(bitstream1, offset1, Length(bitstream1)) == "1001")

solver.add(bitstream2.at(pred_location) == pred_value)

solver.add(bitstream2 == "11001001")
solver.add(SubString(bitstream2, 0, offset2) == "1100")
solver.add(SubString(bitstream2, offset2, offset3 - offset2) == "10")
solver.add(SubString(bitstream2, offset3, 8) == "01")

print(solver.check())
print(solver.model())
