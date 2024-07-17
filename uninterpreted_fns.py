from z3 import *

Color, (red, green, blue) = EnumSort('Color', ('red', 'green', 'blue'))
f = Function('f', IntSort(), IntSort())
x, y = Ints('x y')

# Stuff to synthesize:
# States in the DFA
# Match patterns
# next state
# next lookup offset
# extraction

# Input: 0001001 (some bit string)
# Output: Some segmentation of input into headers: a map,
# Can we canonicalize this map to have keys 1, 2, 3, ... and
# just call it an array. That way output is an array of bitstrings.
# maybe the output is a matrix of bitstrings:
# the x axis is header name, the y axis is field name

solver = Solver()
solver.add(ForAll([x], f(x) > 0))  # f is always positive
solver.add(f(1) == 2)
solver.add(f(2) == f(1) + 1)

print(solver.check())
if solver.check() == sat:
    model = solver.model()
    print(model)
