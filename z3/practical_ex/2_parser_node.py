import random
from z3 import *


"""
spec:
Node0:
extract(field0); // bit<4> field0;
if (field0[3] == 1) {
    goto node1;
} else {
    exit;
}
goto node1;
Node1:
extract(field1); // bit<3> field1;
"""

# ASK XG: Why would pos be anything other than 0 here?
# ASK XG: in other words, in which scenario pos will be 2?
# ASK XG: shouldn't pos always be 0 here?
def node0(Dist, F, I, pos, idx, s):    
   key_expr_field0 = Extract(7 - 4, 4 - 4, I)
   for p  in range(4, -1, -1):
      key_expr_field0 = If(And(Dist[0] == 1, pos == p), Extract(7 - p, 4 - p, I), key_expr_field0)

   key_expr_field1 = Extract(7 - 5, 5 - 5, I)
   for p in range(4, -1, -1):
      key_expr_field1 = If(And(Dist[1] == 1, pos == p), Extract(7 - p, 5 - p, I), key_expr_field1)

   new_node0_f0 = If(And(idx == 0, Dist[0] == 1), key_expr_field0, F[0])
   new_node0_f1 = If(And(idx == 0, Dist[1] == 1), key_expr_field1, F[1])
   post_node0_pos = If(idx == 0, If(Dist[0] == 1, 4, If(Dist[1] == 1, 5, pos)), pos)
#  s.add(Implies(Dist[0] == 1, And(F[0] == key_expr_field0, post_node0_pos == 4)))
#  s.add(Implies(Dist[1] == 1, And(F[1] == key_expr_field1, post_node0_pos == 5)))
#  s.add(Implies(And(Dist[0] == 0, Dist[1] == 0), (post_node0_pos == pos)))
   key_val = BitVec('key_val', 1)

   default_idx_node0 = Int('default_idx_node0')
   # TODO: update idx, current we hardcode the key selection logic
   key_sel = If(And(idx == 0, Dist[0] == 1), Extract(0,0,key_expr_field0), 
               If(And(idx == 0, Dist[1] == 1), Extract(0,0,key_expr_field1), 0))
   ret_idx = If(key_sel == key_val, 1, default_idx_node0)

   return [new_node0_f0, new_node0_f1], post_node0_pos, ret_idx

def node1(Dist, F, I, pos, idx, s):
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
    new_node1_f0 = If(And(idx == 1,Dist[0] == 1), key_expr_field10, F[0])
    new_node1_f1 = If(And(idx == 1,Dist[1] == 1), key_expr_field11, F[1])
   #  s.add(Implies(Dist[0] == 1, And(F[0] == key_expr_field10)))
   #  s.add(Implies(Dist[1] == 1, And(F[1] == key_expr_field11)))
    return [new_node1_f0, new_node1_f1], idx


# define all fields: field0, field1 (Path dependent)
field0 = BitVec('field0', 4)
field1 = BitVec('field1', 3)

solver = Solver()
# initialize_fields
random_value1 = random.randint(0, 15)
solver.add(field0 == random_value1)
random_value2 = random.randint(0, 7)
solver.add(field1 == random_value2)

Out_field0 = BitVec('Out_field0', 4)
Out_field1 = BitVec('Out_field1', 3)

# collect all fields into a list
Fields = [field0, field1] 
Out_Fields = [Out_field0, Out_field1]


# flagij means whether field j is extracted in node i (Path independent)
flag00 = Int('flag00')
flag01 = Int('flag01')
flag10 = Int('flag10')
flag11 = Int('flag11')

Flag0 = [flag00, flag01]
Flag1 = [flag10, flag11]


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

idx = Int('idx')
solver.add(idx == 0)

post_node0_idx = Int('post_node0_idx')
Out_Fields, post_node0, post_node0_idx = node0(Flag0, Fields, I, pos, idx, solver)
# solver.add(Out_Fields[0] == 15)
post_node1_idx = Int('post_node1_idx')
Out_Fields, post_node1_idx = node1(Flag1, Out_Fields, I, post_node0, post_node0_idx, solver)

solver.add(Implies(I == 0b11110000, And(Out_Fields[0] == 0b1111, Out_Fields[1] == 0b000)))
# solver.add(Out_Fields[1] == 0)
solver.add(Out_field0 == Out_Fields[0])
solver.add(Out_field1 == Out_Fields[1])

# Second path
I1 = BitVec('I1', 8)
post_node0_idx_I1 = Int('post_node0_idx_I1')
post_node1_idx_I1 = Int('post_node1_idx_I1')
field0_I1 = BitVec('field0_I1', 4)
field1_I1 = BitVec('field1_I1', 3)
random_value1_I1 = random.randint(0, 15)
solver.add(field0_I1 == random_value1_I1)
random_value2_I1 = random.randint(0, 7)
solver.add(field1_I1 == random_value2_I1)

Out_field0_I1 = BitVec('Out_field0_I1', 4)
Out_field1_I1 = BitVec('Out_field1_I1', 3)

Input_Fields_I1 = [field0_I1, field1_I1]
Out_Fields_I1 = [Out_field0_I1, Out_field1_I1]

post_node0_pos_I1 = Int('post_node0_pos_I1')

Out_Fields_I1, post_node0_pos_I1, post_node0_idx_I1 = node0(Flag0, Input_Fields_I1, I1, pos, idx, solver)
solver.add(post_node0_pos_I1 == 4)
solver.add(post_node0_idx_I1 == 2)
Out_Fields_I1, post_node1_idx_I1 = node1(Flag1, Out_Fields_I1, I, post_node0_pos_I1, post_node0_idx_I1, solver)
solver.add(Implies(I1 == 0b00100000, And(Out_field0_I1 == 0b0010, Out_field1_I1 == random_value2_I1)))

solver.add(I1 == 0b00100000)
solver.add(Out_field0_I1 == Out_Fields_I1[0])
solver.add(Out_field1_I1 == Out_Fields_I1[1])

if solver.check() == sat:
    print("Solution found.")
    model = solver.model()
    print("------After test I1-----")
    print("Out_field0_I1 = (should be 2) =", model[Out_field0_I1])
    print("Out_field1_I1 = (should be", random_value2_I1, ") =", model[Out_field1_I1])
    print("Out_field0 = (should be 15) =", model[Out_field0])
    print("Out_field1 = (should be 0) =", model[Out_field1])
    print("flag00 = (should be 1) =", model[flag00])
    print("flag01 = (should be 0) =", model[flag01])
    print("flag10 = (should be 0) =", model[flag10])
    print("flag11 = (should be 1) =", model[flag11])
    # print("--------------")
    # for var in model:
    #     print(f"{var} = {model[var]}")
else:
    print("No solution found.")