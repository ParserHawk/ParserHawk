from z3 import *

# 000(1) 0000 -> 0001(pkt0) 0000(pkt1)
# 0000 0001 -> 0000(pkt0) 00(pkt2) 01(pkt3)

def node0(I, s):
    ret_expr = Extract(7, 4, I)
    return ret_expr

def node1(I, field0, c1, s):
    new_a1 = BitVec('new_a1', 4)
    new_b1 = BitVec('new_b1', 2)
    new_c1 = BitVec('new_c1', 2)
    
    # Key selection TODO: complete the way to find the key in a brute-force way
    beg_v = Int('beg_v')
    end_v = Int('end_v')
    key_expr = If(beg_v == 0, If(end_v == 0, Extract(0,0,field0), Extract(3,3,field0)), Extract(3,3,field0))

    # s.add(Implies((Extract(0,0,field0) == c1), (new_a1 == Extract(3,0,I))))
    # s.add(Implies((Extract(0,0,field0) != c1), And(new_b1 == Extract(3,2,I), new_c1 == Extract(1,0,I))))
    # TODO: try to compare the key_expr with c1 when they have different size
    s.add(Implies((key_expr == c1), (new_a1 == Extract(3,0,I))))
    s.add(Implies((key_expr != c1), And(new_b1 == Extract(3,2,I), new_c1 == Extract(1,0,I))))
    return new_a1, new_b1, new_c1

# Create a Z3 solver instance
solver = Solver()

# Define two symbolic 8-bit bitvectors
I = BitVec('I', 8)
I1 = BitVec('I1', 8)

field0 = BitVec('field0', 4)
field1 = BitVec('field1', 4)
field2 = BitVec('field2', 2)
field3 = BitVec('field3', 2)

# definition of the state transition key's value
c1 = BitVec('c1', 1)


# Path0: 000(1) 0000 --> 0001(field0) 0000(field1)
solver.add(field0 == node0(I, solver))
field1, field2, field3 = node1(I, field0, c1, solver)

solver.add(I == 0b00010000)
solver.add(Implies(I == 0b00010000, And(field0 == Extract(7,4,I), field1 == Extract(3,0,I))))


field01 = BitVec('field01', 4)
field11 = BitVec('field11', 4)
field21 = BitVec('field21', 2)
field31 = BitVec('field31', 2)

# Path1: 000(0) 0001 --> 0001(field01) 00(field21) 01(field31)
solver.add(field01 == node0(I1, solver))
field11, field21, field31 = node1(I1, field01, c1, solver)

solver.add(I1 == 0b00000001)
solver.add(Implies(I1 == 0b00000001, And(field01 == Extract(7,4,I1), field21 == Extract(3,2,I1), field31 == Extract(1,0,I1))))

if solver.check() == sat:
    model = solver.model()
    
    print("model I =", model[I])
    print("model field0 = (should be 0001)", model[field0])
    print("model field1 = (should be 0000)", model[field1])
    print("model field2 = (can be anything)", model[field2])
    print("model field3 = (can be anything)", model[field3])
    
    print("model I1 =", model[I1])
    print("model field01 = (should be 0000)", model[field01])
    print("model field11 = (can be anything)", model[field11])
    print("model field21 = (should be 00)", model[field21])
    print("model field31 = (should be 01)", model[field31])
    
    print("value of the key model c1 (we should focus), its value should be 1 =", model[c1])
    print(model)
else:
    print("No solution found.")

