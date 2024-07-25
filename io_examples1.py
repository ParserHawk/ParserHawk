from z3 import *

### # parse unconditionally into two headers of 4 bits each
### # uses: one state with two extracts, or two states with one extract each
### 10001001 -> ['1000', '1001']
### 11001001 -> ['1100', '1001']
### 
### 
### # DFA for this
### State | Lookup | Extract | Next State |
### ---------------------------------------
### 1     | *      | 0,4     | 2          |
### 2     | *      | 0,4     | END        | 


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
m=solver.model()
print(m[bitstream1])
print(m[bitstream2])
print(m[offset])
