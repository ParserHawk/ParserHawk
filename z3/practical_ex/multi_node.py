from z3 import *

"""
spec:
Node0:
extract(field0);
goto node1;
Node1:
extract(field1);
"""

def node0(Dist, F, I, pos, s):
    key_expr_field0 = If(And(Dist[0] == 1, pos == 0), Extract(7, 4, I), 
                  If(And(Dist[0] == 1, pos == 1), Extract(7 - 1, 4 - 1, I),
                     If(And(Dist[0] == 1, pos == 2), Extract(7 - 2, 4 - 2, I),
                        If(And(Dist[0] == 1, pos == 3), Extract(7 - 3, 4 - 3, I),
                           If(And(Dist[0] == 1, pos == 4), Extract(7 - 4, 4 - 4, I),
                              Extract(7 - 4, 4 - 4, I))))))
    key_expr_field1 = If(And(Dist[1] == 1, pos == 0), Extract(7, 5, I), 
                  If(And(Dist[1] == 1, pos == 1), Extract(7 - 1, 5 - 1, I),
                     If(And(Dist[1] == 1, pos == 2), Extract(7 - 2, 5 - 2, I),
                        If(And(Dist[1] == 1, pos == 3), Extract(7 - 3, 5 - 3, I),
                           If(And(Dist[1] == 1, pos == 4), Extract(7 - 4, 5 - 4, I),
                              Extract(7 - 5, 5 - 5, I))))))
    post_node0_pos = Int('post_node0_pos')
    s.add(Implies(Dist[0] == 1, And(F[0] == key_expr_field0, post_node0_pos == 4)))
    s.add(Implies(Dist[1] == 1, And(F[1] == key_expr_field1, post_node0_pos == 5)))
    s.add(Implies(And(Dist[0] == 0, Dist[1] == 0), (post_node0_pos == pos)))
    return F, post_node0_pos

def node1(Dist, F, I, pos, s):
    pre_F0 = F[0]
    pre_F1 = F[1]
    key_expr_field10 = If(And(Dist[0] == 1, pos == 0), Extract(7, 4, I), 
                  If(And(Dist[0] == 1, pos == 1), Extract(7 - 1, 4 - 1, I),
                     If(And(Dist[0] == 1, pos == 2), Extract(7 - 2, 4 - 2, I),
                        If(And(Dist[0] == 1, pos == 3), Extract(7 - 3, 4 - 3, I),
                           If(And(Dist[0] == 1, pos == 4), Extract(7 - 4, 4 - 4, I),
                              pre_F0)))))
    key_expr_field11 = If(And(Dist[1] == 1, pos == 0), Extract(7, 5, I), 
                  If(And(Dist[1] == 1, pos == 1), Extract(7 - 1, 5 - 1, I),
                     If(And(Dist[1] == 1, pos == 2), Extract(7 - 2, 5 - 2, I),
                        If(And(Dist[1] == 1, pos == 3), Extract(7 - 3, 5 - 3, I),
                           If(And(Dist[1] == 1, pos == 4), Extract(7 - 4, 5 - 4, I),
                              pre_F1)))))
    s.add(Implies(Dist[0] == 1, And(F[0] == key_expr_field10)))
    s.add(Implies(Dist[1] == 1, And(F[1] == key_expr_field11)))
    return F


# define all fields: field0, field1 (Path dependent)
field0 = BitVec('field0', 4)
field1 = BitVec('field1', 3)

# collect all fields into a list
Fields = [field0, field1] 

# flagij means whether field j is extracted in node i (Path independent)
flag00 = Int('flag00')
flag01 = Int('flag01')
flag10 = Int('flag10')
flag11 = Int('flag11')

Flag0 = [flag00, flag01]
Flag1 = [flag10, flag11]

solver = Solver()

# at most one extraction per node
solver.add(Sum(Flag0) <= 1)
solver.add(Sum(Flag1) <= 1)

solver.add(Or(Flag0[0] == 0, Flag0[0] == 1))
solver.add(Or(Flag0[1] == 0, Flag0[1] == 1))

solver.add(Or(Flag1[0] == 0, Flag1[0] == 1))
solver.add(Or(Flag1[1] == 0, Flag1[1] == 1))

# input bit vector
I = BitVec('I', 8)

pos = Int('pos')
solver.add(pos == 0)

post_node0 = Int('post_node0')

solver.add(I == 0b11110000)
Fields, post_node0 = node0(Flag0, Fields, I, pos, solver)
Fields = node1(Flag1, Fields, I, post_node0, solver)
solver.add(Implies(I == 0b11110000, And(Fields[0] == 0b1111, Fields[1] == 0b000)))


if solver.check() == sat:
    print("Solution found.")
    model = solver.model()
    print("post_node0 (should be 4) =", model[post_node0])
    print("field0 = (should be 15) =", model[field0])
    print("field1 = (should be 0) =", model[field1])
    print("flag00 = (should be 1) =", model[flag00])
    print("flag01 = (should be 0) =", model[flag01])
    print("flag10 = (should be 0) =", model[flag10])
    print("flag11 = (should be 1) =", model[flag11])
    print("--------------")
    for var in model:
        print(f"{var} = {model[var]}")
else:
    print("No solution found.")