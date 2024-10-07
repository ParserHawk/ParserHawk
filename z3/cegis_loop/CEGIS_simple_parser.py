from z3 import *

from bitarray import bitarray
import random

"""
spec:
first 4-bit --> field1
next 4-bit --> field0

0000 1111 -> field1 == 0000, field0 == 1111
1111 0000 -> field1 == 1111, field0 == 0000

"""

def node0(Dist, F, I, idx, s):
    key_expr_field0 = Extract(7, 4, I)
    key_expr_field1 = Extract(7, 4, I)
    new_node0_f0 = If(And(idx == 0, Dist[0] == 1), key_expr_field0, F[0])
    new_node0_f1 = If(And(idx == 0, Dist[1] == 1), key_expr_field1, F[1])
    ret_idx = idx + 1

    return [new_node0_f0, new_node0_f1], ret_idx

def node1(Dist, F, I, idx, s):
    key_expr_field0 = Extract(3, 0, I)
    key_expr_field1 = Extract(3, 0, I)
    new_node1_f0 = If(And(idx == 1, Dist[0] == 1), key_expr_field0, F[0])
    new_node1_f1 = If(And(idx == 1, Dist[1] == 1), key_expr_field1, F[1])

    return [new_node1_f0, new_node1_f1]

# Function to generate temporary BitVec variables for each iteration
def temporary_bitvec_for_counterexample(I_val, initial_f0, initial_f1):
    # Dynamically create new BitVec variable for this iteration
    temp_bv = BitVec(f'temp_bv_{I_val}', 8)  # 8-bit for example, can be adjusted
    input_field0 = BitVec(f'input_field0_{I_val}', 4)
    input_field1 = BitVec(f'input_field1_{I_val}', 4)
    
    # Define constraints for this temporary BitVec based on the counterexample
    constraint = []
    constraint.append(temp_bv == I_val)  # Constraint depends on the counterexample
    constraint.append(input_field0 == initial_f0)
    constraint.append(input_field1 == initial_f1)
    
    return temp_bv, input_field0, input_field1, constraint

def implementation(Flag0, Flag1, Input_bitstream, idx, initial_f0, initial_f1, s):
    
    temp_bv, input_field0, input_field1, temp_constraint = temporary_bitvec_for_counterexample(Input_bitstream, initial_f0, initial_f1)
    s.add(temp_constraint)

    Input_Fields = [input_field0, input_field1]
    Out_Fields, idx_after_node0 = node0(Flag0, Input_Fields, temp_bv, idx, s)
    Out_Fields = node1(Flag1, Out_Fields, temp_bv, idx_after_node0, s)
    return Out_Fields

# Input_bitstream is a bitVec var in z3
# TODO: should generate the specification automatically
def specification(Input_bitstream, initial_f0, initial_f1):
    # out_field1 = BitVec(f'out_field0_{I_val}', 4)
    O_field0 = Extract(3, 0, Input_bitstream)
    idx0 = 1
    O_field1 = If(Extract(0, 0, O_field0) == 1, Extract(7, 4, Input_bitstream), Extract(7, 4, Input_bitstream))
    idx1 = If(Extract(0, 0, O_field0) == 1, 1, 1)
    return [O_field0, O_field1], [idx0, idx1]

# This function is used for formatting purpose
def get_int_representation(l):
    ret_l = []
    for mem in l:
        if isinstance(mem, bitarray):
            ret_l.append(int(mem.to01(), 2))
        else:
            ret_l.append(int(mem))
    return ret_l

def spec(Input_bitstream):
    # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
    l = [int(Input_bitstream[4 : 8], 2), int(Input_bitstream[0 : 4], 2)]
    return l

def synthesis_step(cexamples):
    print("Enter synthsis phase")
    # Define all variables
    # Create a solver to synthesize f(x)
    s = Solver()
    s.reset()

    flag00 = Int('flag00')
    flag01 = Int('flag01')
    flag10 = Int('flag10')
    flag11 = Int('flag11')
    Flag0 = [flag00, flag01]
    Flag1 = [flag10, flag11]
    s.add(Sum(Flag0) <= 1)
    s.add(Sum(Flag1) <= 1)
    s.add(flag00 + flag10 <= 1)
    s.add(flag01 + flag11 <= 1)
    s.add(Or(Flag0[0] == 0, Flag0[0] == 1))
    s.add(Or(Flag0[1] == 0, Flag0[1] == 1))
    s.add(Or(Flag1[0] == 0, Flag1[0] == 1))
    s.add(Or(Flag1[1] == 0, Flag1[1] == 1))

    idx = Int('idx')
    s.add(idx == 0)

    if not cexamples:
        # If no counterexamples exist yet, try to find any function
        print("Counterexample set cannot be empty")
        sys.exit(1)
    else:
        for Input_bitval in cexamples:
            # input bit stream I = [0,0,0,0,...0]
            # Out_spec = spec(I)
            # Out_impl = impl(I, initial_val_of_input_fields)
            initial_random_value_field0 = random.randint(0, 2**4 - 1)
            initial_random_value_field1 = random.randint(0, 2**4 - 1)
            impl_out = implementation(Flag0, Flag1, Input_bitval, idx, initial_random_value_field0, initial_random_value_field1, s)
            spec_out = spec(format(Input_bitval, '08b'))
            s.add(impl_out[0] == spec_out[0])
            s.add(impl_out[1] == spec_out[1])

    # Check if the constraints are satisfiable
    if s.check() == sat:
        print("s.check() == sat")
        model = s.model()
        flag00_value = model[flag00]
        if flag00_value is not None:
            flag00_value = flag00_value.as_long()
        else:
            flag00_value = 0
        flag01_value = model[flag01]
        if flag01_value is not None:
            flag01_value = flag01_value.as_long()
        else:
            flag01_value = 0
        flag10_value = model[flag10]
        if flag10_value is not None:
            flag10_value = flag10_value.as_long()
        else:
            flag10_value = 0
        flag11_value = model[flag11]
        if flag11_value is not None:
            flag11_value = flag11_value.as_long()
        else:
            flag11_value = 0

        return flag00_value, flag10_value, flag01_value, flag11_value  # Return synthesized function coefficients
    else:
        # No valid solution found for current counterexamples
        print("No solution found for the given counterexamples.")
        return None

def verification_step(flag00_value, flag10_value, flag01_value, flag11_value):
    print("Enter verification phase")
    # Try to find a counterexample where f(x) != g(x)
    x = BitVec('x', 8)
    s = Solver()

    # Constraint: f(x) = coeff * x + bias should equal g(x) = x + 1
    flag00 = Int('flag00')
    flag01 = Int('flag01')
    flag10 = Int('flag10')
    flag11 = Int('flag11')
    Flag0 = [flag00, flag01]
    Flag1 = [flag10, flag11]
    s.add(flag00 == flag00_value)
    s.add(flag01 == flag01_value)
    s.add(flag10 == flag10_value)
    s.add(flag11 == flag11_value)
    idx = Int('idx')
    s.add(idx == 0)
    # TODO: sometimes, these initial values may affect the final outcome
    initial_f0 = random.randint(0, 2**4 - 1)
    initial_f1 = random.randint(0, 2**4 - 1)
    O_Impl = implementation(Flag0, Flag1, x, idx, initial_f0, initial_f1, s)
    O_Spec, Modify_idx = specification(x, initial_f0, initial_f1)
    s.add(Or(And(O_Impl[0] != O_Spec[0], Modify_idx[0] == 1), And(O_Impl[1] != O_Spec[1], Modify_idx[1] == 1)))  # Find a mismatch between f(x) and g(x)

    if s.check() == sat:
        model = s.model()
        return model[x].as_long()  # Return the counterexample value for x
    else:
        return None  # No counterexample found, the candidate function is valid

def cegis_loop():
    cexamples = [0] # Start with one counterexamples  
    # 0000 0000 
    # impl:
    # first 4-bit --> field0
    # next 4-bit --> field1
    # spec:
    # first 4-bit --> field1
    # next 4-bit --> field0
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
        # coeff, bias = candidate
        # print(f"Candidate function: f(x) = {coeff}x + {bias}")

        # # Verification step: check if the candidate is valid
        flag00_value, flag10_value, flag01_value, flag11_value =  candidate
        print(f"Synthesis solution found, flag00 = {flag00_value}, flag01 = {flag01_value}, flag10 = {flag10_value}, flag11 = {flag11_value}")
        cexample = verification_step(flag00_value, flag10_value, flag01_value, flag11_value)
        if cexample is None:
            print(f"Valid function found, flag00 = {flag00_value}, flag01 = {flag01_value}, flag10 = {flag10_value}, flag11 = {flag11_value}")
            return
        else:
            print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round

# Run the CEGIS loop
cegis_loop()