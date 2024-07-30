from z3 import *

### parse differently depending on the value of the 4th bit from left
### uses three states: first has an extract and select. second has a single extract. third has two extracts.
### 10001001 -> ['1000', '1001']
### 10011001 -> ['1001', '10', '01']

solver = Solver()

# input bit streams
input_stream1 = "10001001"
input_stream2 = "10011001" # the decision bit is present at index 3 (the decision bit can be moved around anywhere)
# input_stream2 = "10101001" # can comment out line above and uncomment this to try a new string with a different decision bit location, don't forget to also change the string value below when applying offsets

# z3 solver variables
input1 = String('input1')
input2 = String('input2')
offset1 = Int('offset1') # offset for first bitstream
offset2 = Int('offset2') # offset for second bitstream
offset3 = Int('offset3') # offset for second bitstream
decision_bit_location = Int('decision_bit_location')

# assign input bit streams to z3 variables
solver.add(input1 == input_stream1)
solver.add(input2 == input_stream2)

# add basic constraints on location of offsets
solver.add(decision_bit_location >= 0, decision_bit_location < Length(input1))
solver.add(offset1 >= 0, offset1 < Length(input1))
solver.add(offset2 >= 0, offset2 < Length(input2))
solver.add(offset3 > offset2, offset3 < Length(input2))

# Add constraint to determine the decision bit location. 
# Simple logic where we explicitly provide that the expected decision bit is 1 bit in length
# And also provide the offset logic depending on if the decision bit is 1 or 0
# So the solver here finds the decision bit location and outputs it along with the offsets calculated
solver.add(
    # Syntax of If statement
    # If (cond, if_true, else)
    If(
        # Condition - if decision bit in string1 is 0 and in string2 is 1
        And(SubString(input1, decision_bit_location, 1) == StringVal('0'), SubString(input2, decision_bit_location, 1) == StringVal('1')),
        
        # Offset logic
        And(SubString(input1, 0, offset1) == StringVal('1000'),
           SubString(input1, offset1, Length(input1) - offset1) == StringVal('1001'),
           SubString(input2, 0, offset2) == StringVal('1001'), # change value here accordingly when changing inputstream2 value
           SubString(input2, offset2, offset3 - offset2) == StringVal('10'),
           SubString(input2, offset3, Length(input2) - offset3) == StringVal('01')),

        # Constraint returns false for all bits where the corresponding bit in string1 and string2 are not the same
        False
))

# Print out the results after the solver evaluates
if solver.check() == sat:
    model = solver.model()
    print("Decision Bit Index: ", model[decision_bit_location])
    
    print("\nInput Stream 1:", model[input1])
    print("Offset1: ", model[offset1])

    print("\nInput Stream 2:", model[input2])
    print("Offset2: ", model[offset2])
    print("Offset3: ", model[offset3])
else:
    print("No solution found")

