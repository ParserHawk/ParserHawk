from z3 import *

"""
spec:
in parser node 0: extract(field0) where field0 is a 4-bit variable.
We want z3 to find the synthesis result to show that node 0 should 
extract field0 by setting flag0 to 1
"""

def node0(Dist, F, I, s):
    # TODO: find a better way to encode extraction behavior
    key_expr = If(Dist[0] == 1, Extract(7, 4, I), 
                  If(Dist[1] == 1, ZeroExt(1, Extract(7, 5, I)), 
                       If(Dist[2] == 1, ZeroExt(2, Extract(7, 6, I)), 0b0000)))
    s.add(Implies(Dist[0] == 1, F[0] == key_expr))
    s.add(Implies(Dist[0] == 0, F[0] != key_expr))
    s.add(Implies(Dist[1] == 1, F[1] == Extract(2, 0,key_expr)))
    s.add(Implies(Dist[1] == 0, F[1] != Extract(2, 0,key_expr)))
    s.add(Implies(Dist[2] == 1, F[2] == Extract(1, 0,key_expr)))
    s.add(Implies(Dist[2] == 0, F[2] != Extract(1, 0,key_expr)))
    return F

# field0, field1, field2
field0 = BitVec('field0', 4)
field1 = BitVec('field1', 3)
field2 = BitVec('field2', 2)

Fields = [field0, field1, field2] # record the value of F

flag0 = Int('flag0')
flag1 = Int('flag1')
flag2 = Int('flag2')

# Central distributor: 
# flag0 == 1 <-> field0 is extracted in node 0
# flag1 == 1 <-> field1 is extracted in node 0
# flag2 == 1 <-> field2 is extracted in node 0
Flag = [flag0, flag1, flag2]

I = BitVec('I', 8)

solver = Solver()
solver.add(Or(Flag[0] == 1, Flag[0] == 0))
solver.add(Or(Flag[1] == 1, Flag[1] == 0))
solver.add(Or(Flag[2] == 1, Flag[2] == 0))
solver.add(Sum(Flag) <= 1)

# TODO: find a better way to try all possible input/output values
solver.add(I == 0b11110000)
solver.add(Implies(I == 0b11110000, node0(Flag, Fields, I, solver)[0] == Extract(7,4,I)))

I1 = BitVec('I1', 8)
# field0, field1, field2
field00 = BitVec('field00', 4)
field11 = BitVec('field11', 3)
field22 = BitVec('field22', 2)

Fields1 = [field00, field11, field22] # record the value of F

solver.add(I1 == 0b11100000)
solver.add(Implies(I1 == 0b11100000, node0(Flag, Fields1, I1, solver)[0] == Extract(7,4,I1)))


if solver.check() == sat:
    model = solver.model()
    print("Output results in model (used as a unit test)")
    print("I = (should be 240)", model[I])
    print("field0 = (should be 15)", model[field0])
    print("I1 = (should be 224)", model[I1])
    print("field00 = (should be 14)", model[field00])
    print("flag0 = (should be 1)", model[flag0])
    print("flag1 = (should be 0)", model[flag1])
    print("flag2 = (should be 0)", model[flag2])
    # for var in model:
    #     print(f"{var} = {model[var]}")
else:
    print("No solution found.")