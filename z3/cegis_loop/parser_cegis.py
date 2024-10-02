from z3 import *

import sys
'''
spec:
Node0:
extract(field0); // bit<4> field0;
'''

size_of_key = 2
def node0(Dist, F, I, pos, idx, alloc_matrix, s):
    # Acc = nil
    # For x in array:
    #     Acc = If(Acc, x[0], x[1])
    # key_expr_field0 = F[0]
    # for i in range(len(size)):
    #     key_expr_field0 = If(cond(i), Extract(i), key_expr_field0)
    key_expr_field0 = If(And(Dist[0] == 1, pos == 0), Extract(13, 6, I),
                        If(And(Dist[0] == 1, pos == 1), Extract(12, 5, I),
                        If(And(Dist[0] == 1, pos == 2), Extract(11, 4, I),
                        If(And(Dist[0] == 1, pos == 3), Extract(10, 3, I),
                        If(And(Dist[0] == 1, pos == 4), Extract(9, 2, I),
                        If(And(Dist[0] == 1, pos == 5), Extract(8, 1, I),
                        If(And(Dist[0] == 1, pos == 6), Extract(7, 0, I),
                                F[0])))))))

    key_expr_field1 = If(And(Dist[1] == 1, pos == 0), Extract(13, 10, I),
                        If(And(Dist[1] == 1, pos == 1), Extract(12, 9, I),
                        If(And(Dist[1] == 1, pos == 2), Extract(11, 8, I),
                        If(And(Dist[1] == 1, pos == 3), Extract(10, 7, I),
                        If(And(Dist[1] == 1, pos == 4), Extract(9, 6, I),
                        If(And(Dist[1] == 1, pos == 5), Extract(8, 5, I),
                        If(And(Dist[1] == 1, pos == 6), Extract(7, 4, I),
                        If(And(Dist[1] == 1, pos == 7), Extract(6, 3, I),
                        If(And(Dist[1] == 1, pos == 8), Extract(5, 2, I),
                        If(And(Dist[1] == 1, pos == 9), Extract(4, 1, I),
                        If(And(Dist[1] == 1, pos == 10), Extract(3, 0, I),
                                F[1])))))))))))
    key_expr_field2 = If(And(Dist[2] == 1, pos == 0), Extract(13, 8, I),
                        If(And(Dist[2] == 1, pos == 1), Extract(12, 7, I),
                        If(And(Dist[2] == 1, pos == 2), Extract(11, 6, I),
                        If(And(Dist[2] == 1, pos == 3), Extract(10, 5, I),
                        If(And(Dist[2] == 1, pos == 4), Extract(9, 4, I),
                        If(And(Dist[2] == 1, pos == 5), Extract(8, 3, I),
                        If(And(Dist[2] == 1, pos == 6), Extract(7, 2, I),
                        If(And(Dist[2] == 1, pos == 7), Extract(6, 1, I),
                        If(And(Dist[2] == 1, pos == 8), Extract(5, 0, I),
                                F[2])))))))))

    new_node0_f0 = If(And(idx == 0, Dist[0] == 1), key_expr_field0, F[0])
    new_node0_f1 = If(And(idx == 0, Dist[1] == 1), key_expr_field1, F[1])
    new_node0_f2 = If(And(idx == 0, Dist[2] == 1), key_expr_field2, F[2])
    
    # Update position
    post_node0_pos = If(idx == 0, If(Dist[0] == 1, pos+8, If(Dist[1] == 1, pos+4, If(Dist[2] == 1, pos+6, pos))), pos)

    # Do key selection
    dummy = BitVec('dummy', 1)
    s.add(dummy == 0)
    key_sel = None
    for j in range(len(alloc_matrix[0]) - 1, -1, -1):
        if key_sel == None:
            key_sel = If(alloc_matrix[0][j] == 0, Extract(j,j,new_node0_f0),dummy)
        else:
            key_sel = If(alloc_matrix[0][j] == 0, Concat(key_sel, Extract(j,j,new_node0_f0)), Concat(dummy, key_sel))
    for j in range(len(alloc_matrix[1]) - 1, -1, -1):
        key_sel = If(alloc_matrix[1][j] == 0, Concat(key_sel, Extract(j,j,new_node0_f1)), Concat(dummy, key_sel))
    for j in range(len(alloc_matrix[2]) - 1, -1, -1):
        key_sel = If(alloc_matrix[2][j] == 0, Concat(key_sel, Extract(j,j,new_node0_f2)), Concat(dummy, key_sel))

    # State transition
    key_val0_node0 = BitVec('key_val0_node0', size_of_key)
    tran_idx0_node0 = Int('tran_idx0_node0')
    key_val1_node0 = BitVec('key_val1_node0', size_of_key)
    tran_idx1_node0 = Int('tran_idx1_node0')
    default_idx_node0 = Int('default_idx_node0')
    # len of state transition key <= threshold
    ret_idx = If(idx == 0, If(Extract(size_of_key - 1,0,key_sel) == key_val0_node0, tran_idx0_node0, 
                 If(Extract(size_of_key - 1,0,key_sel) == key_val1_node0, tran_idx1_node0,default_idx_node0)), idx)
    return [new_node0_f0, new_node0_f1, new_node0_f2], post_node0_pos, ret_idx

def synthesis_step(cexamples):
    print("Enter synthsis phase")
    # Define f(x) = f_coeff * x + f_bias

    pos = Int('pos')
    idx = Int('idx')

    # Create a solver to synthesize f(x)
    solver = Solver()
    solver.reset()  # reset solver's internal state
    solver.add(pos == 0)
    solver.add(idx == 0)

    flag_0_0 = Int('flag_0_0')
    flag_0_1 = Int('flag_0_1')
    flag_0_2 = Int('flag_0_2')
    flag_1_0 = Int('flag_1_0')
    flag_1_1 = Int('flag_1_1')
    flag_1_2 = Int('flag_1_2')
    flag_2_0 = Int('flag_2_0')
    flag_2_1 = Int('flag_2_1')
    flag_2_2 = Int('flag_2_2')
    flag_3_0 = Int('flag_3_0')
    flag_3_1 = Int('flag_3_1')
    flag_3_2 = Int('flag_3_2')
    Flag0 = [flag_0_0, flag_0_1, flag_0_2]
    Flag1 = [flag_1_0, flag_1_1, flag_1_2]
    Flag2 = [flag_2_0, flag_2_1, flag_2_2]
    Flag3 = [flag_3_0, flag_3_1, flag_3_2]
    solver.add(Sum(Flag0) <= 1)
    solver.add(Sum(Flag1) <= 1)
    solver.add(Sum(Flag2) <= 1)
    solver.add(Sum(Flag3) <= 1)
    solver.add(flag_0_0 + flag_1_0 + flag_2_0 + flag_3_0 <= 1)
    solver.add(flag_0_1 + flag_1_1 + flag_2_1 + flag_3_1 <= 1)
    solver.add(flag_0_2 + flag_1_2 + flag_2_2 + flag_3_2 <= 1)
    solver.add(Or(Flag0[0] == 0, Flag0[0] == 1))
    solver.add(Or(Flag0[1] == 0, Flag0[1] == 1))
    solver.add(Or(Flag0[2] == 0, Flag0[2] == 1))
    solver.add(Or(Flag1[0] == 0, Flag1[0] == 1))
    solver.add(Or(Flag1[1] == 0, Flag1[1] == 1))
    solver.add(Or(Flag1[2] == 0, Flag1[2] == 1))
    solver.add(Or(Flag2[0] == 0, Flag2[0] == 1))
    solver.add(Or(Flag2[1] == 0, Flag2[1] == 1))
    solver.add(Or(Flag2[2] == 0, Flag2[2] == 1))
    solver.add(Or(Flag3[0] == 0, Flag3[0] == 1))
    solver.add(Or(Flag3[1] == 0, Flag3[1] == 1))
    solver.add(Or(Flag3[2] == 0, Flag3[2] == 1))

    # if field0_0 == i --> field0[0] is used as a key value in node i
    field0_0 = Int('field0_0')
    field0_1 = Int('field0_1')
    field0_2 = Int('field0_2')
    field0_3 = Int('field0_3')
    field0_4 = Int('field0_4')
    field0_5 = Int('field0_5')
    field0_6 = Int('field0_6')
    field0_7 = Int('field0_7')
    field1_0 = Int('field1_0')
    field1_1 = Int('field1_1')
    field1_2 = Int('field1_2')
    field1_3 = Int('field1_3')
    field2_0 = Int('field2_0')
    field2_1 = Int('field2_1')
    field2_2 = Int('field2_2')
    field2_3 = Int('field2_3')
    field2_4 = Int('field2_4')
    field2_5 = Int('field2_5')
    alloc_matrix = [[field0_0, field0_1, field0_2, field0_3, field0_4, field0_5, field0_6, field0_7], 
                    [field1_0, field1_1, field1_2, field1_3], 
                    [field2_0, field2_1, field2_2, field2_3, field2_4, field2_5]]

    if not cexamples:
        # If no counterexamples exist yet, try to find any function
        print("Counterexample set should not be empyt")
        sys.exit()
    else:
        # Add constraints: f(x) should equal g(x) = x for all counterexamples
        for Input_value_bitstream0 in cexamples:
            solver.push()
            Input_bitstream_path0 = BitVec('Input_bitstream_path0', 8)
            solver.add(Input_bitstream_path0 == int(Input_value_bitstream0, 2))
            Input_Fields_path0 = [BitVec('f0', 8), BitVec('f0', 4), BitVec('f0', 6)]
            Out_Fields_path0, position_after_node0_path0, idx_after_node0_path0 = node0(Flag0, Input_Fields_path0, Input_bitstream_path0, pos, idx, alloc_matrix, solver)
            solver.add(Out_Fields_path0[0] == Input_bitstream_path0)  # g(x) = x
            solver.pop()

    # Check if the constraints are satisfiable
    if solver.check() == sat:
        print("s.check() == sat")
        model = solver.model()
        print("model =", model)
        # Deal with the situation where model does not output everything
        # coeff_value = model[f_coeff]
        # if coeff_value is not None:
        #     coeff_value = coeff_value.as_long()
        # else:
        #     coeff_value = 0
        # bias_value = model[f_bias]
        # if bias_value is not None:
        #     bias_value = bias_value.as_long()
        # else:
        #     bias_value = 0
        # print("coeff_value =", coeff_value, "bias_value =", bias_value)

        # return coeff_value, bias_value  # Return synthesized function coefficients
    else:
        # No valid solution found for current counterexamples
        print("No solution found for the given counterexamples.")
        return None

def verification_step(coeff, bias):
    print("Enter verification phase")
    # Try to find a counterexample where f(x) != g(x)
    x = Int('x')
    s = Solver()

    # Constraint: f(x) = coeff * x + bias should equal g(x) = x + 1
    s.add(coeff * x + bias != x + 1)  # Find a mismatch between f(x) and g(x)

    if s.check() == sat:
        model = s.model()
        return model[x].as_long()  # Return the counterexample value for x
    else:
        return None  # No counterexample found, the candidate function is valid

def cegis_loop():
    cexamples = ['0000']  # Start with no counterexamples
    maxIter = 10 # Alternatively, we can set it to be # input space.
    for i in range(maxIter):
        print("")
        print("cexamples =", cexamples)
        # Synthesis step: generate a new candidate solution f(x)
        candidate = synthesis_step(cexamples)
        print("where candidate is none or not", candidate == None)
        if candidate is None:
            print("Synthesis failed, no valid function found.")
            return

        coeff, bias = candidate
        print(f"Candidate function: f(x) = {coeff}x + {bias}")

        # Verification step: check if the candidate is valid
        cexample = verification_step(coeff, bias)
        if cexample is None:
            print(f"Valid function found: f(x) = {coeff}x + {bias}")
            return
        else:
            print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round

# Run the CEGIS loop
cegis_loop()