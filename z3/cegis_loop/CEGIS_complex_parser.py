from z3 import *

from bitarray import bitarray
import random
import sys
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# Now you can import the library from Folder B
from practical_ex.code_generation import *

"""
XXXX 0011 XXXXXX
XXXX 1111 XXXXXX
XXXX YYYY XXXXXX 
spec:
Node0:
extract(ethernet); // bit<8> ethernet;
if (ethernet[4:7] == 0b1111) {
    goto node1;
} else if (ethernet[4:7] == 0b0011){
    goto node2
} else {
    exit;
}

Node1:
extract(ipv4); // bit<4> ipv4;

Node2:
extract(ipv6); // bit<6> ipv6;
"""

input_bit_stream_size = 14
num_parser_nodes = 4
num_pkt_fields = 3
pkt_field_size_list = [8, 4, 6]
lookahead_window_size = 2
size_of_key = 2
num_transitions = 2

def dynamic_extract_loop(pos, I, Dist, F, field_size, field_id):
    # Initial expression is the fallback value F[0]
    expr = F
    
    # Loop to construct nested If conditions for Extract
    for i in range(input_bit_stream_size - field_size + 1):
        # Compute start and end indices for the extract operation
        start = input_bit_stream_size - 1 - i
        end = start - (field_size - 1)
        if end < 0:
            break
        # Construct the If expression with And conditions
        expr = If(And(Dist[field_id] == 1, pos == i), Extract(start, end, I), expr)
    
    return expr

def generate_key_expr_list(pos, I, Dist, F, alloc_matrix):
    ret_l = []
    for i in range(len(alloc_matrix)):
        ret_l.append(dynamic_extract_loop(pos, I, Dist, F[i], len(alloc_matrix[i]), field_id=i))
    return ret_l

def generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, node_id):
    ret_l = []
    for i in range(len(alloc_matrix)):
        ret_l.append(If(And(idx == node_id, Dist[i] == 1), key_expr_list[i], F[i]))
    return ret_l

def generate_tran_key(alloc_matrix, node_id, update_field_val_l, 
                      post_node_pos, Lookahead, I, s):
    dummy = BitVec('dummy', 1)
    s.add(dummy == 0)
    key_sel = None
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i])):
            if key_sel == None:
                key_sel = If(alloc_matrix[i][j] == node_id, Extract(j,j,update_field_val_l[0]),dummy)    
            else:
                key_sel = If(alloc_matrix[i][j] == node_id, Concat(key_sel, Extract(j,j,update_field_val_l[i])), Concat(dummy, key_sel))    
    
    for j in range(lookahead_window_size):
        for i in range(input_bit_stream_size):
            if input_bit_stream_size - 1 - i - j < 0:
                break
            key_sel = If(And(Lookahead[j] == 1, post_node_pos == i), Concat(key_sel, Extract(input_bit_stream_size - 1 - i - j, input_bit_stream_size - 1 - i - j, I)), Concat(dummy, key_sel))   
    # for j in range(max_lookahead_bit):
    #     key_sel = If(And(Lookahead[j] == 1, post_node_pos == 8), Concat(key_sel, Extract(13 - 8 - j, 13 - 8 - j,I)), Concat(dummy, key_sel))

    return key_sel

def post_node_pos(idx, Dist, node_id, alloc_matrix, pos):
    # Start with the base case: if none of Dist[i] == 1 apply, return pos
    result = pos
    
    # Loop over the indices and build the nested If conditions
    for i in range(len(Dist) - 1, -1, -1):  # Reverse order to build nested If from the inside out
        result = If(Dist[i] == 1, pos + len(alloc_matrix[i]), result)
    
    # Add the outermost condition for idx
    return If(idx == node_id, result, pos)

def generate_return_idx(key_val_list, tran_idx_list, default_idx_node1, num_transitions, size_of_key, key_sel, idx, node_id):
    ret_idx = default_idx_node1  # Default case
    for i in reversed(range(num_transitions)):
        ret_idx = If(Extract(size_of_key - 1, 0, key_sel) == key_val_list[i], tran_idx_list[i], ret_idx)

    # Final state transition for idx == 1
    ret_idx = If(idx == node_id, ret_idx, idx)
    return ret_idx

# Should be OK
def node0(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, tran_idx_list, default_idx_node, s):
    nodeID = 0
    key_expr_list = generate_key_expr_list(pos, I, Dist, F, alloc_matrix)
    update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, node_id = nodeID)
    post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
    key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
                                update_field_val_l = update_field_val_l, 
                                post_node_pos = post_pos, Lookahead=Lookahead, I = I, s = s)
    
    # State transition
    key_val_list = key_val_list
    tran_idx_list = tran_idx_list
    default_idx_node = default_idx_node
    # Build the state transition logic with a for loop
    ret_idx = generate_return_idx(key_val_list, tran_idx_list, 
                                  default_idx_node, num_transitions, size_of_key, key_sel,
                                  idx, node_id = nodeID)
    
    return update_field_val_l, post_pos, ret_idx
# Should be OK
def node1(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, tran_idx_list, default_idx_node, s):
    nodeID = 1
    key_expr_list = generate_key_expr_list(pos, I, Dist, F, alloc_matrix)
    update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, node_id = nodeID)
    post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
    key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
                                update_field_val_l = update_field_val_l, 
                                post_node_pos = post_pos, Lookahead=Lookahead, I = I, s = s)
    
    # State transition
    key_val_list = key_val_list
    tran_idx_list = tran_idx_list
    default_idx_node = default_idx_node
    # Build the state transition logic with a for loop
    ret_idx = generate_return_idx(key_val_list, tran_idx_list, 
                                  default_idx_node, num_transitions, size_of_key, key_sel,
                                  idx, node_id = nodeID)
    
    return update_field_val_l, post_pos, ret_idx
# Should be OK
def node2(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, tran_idx_list, default_idx_node, s):
    nodeID = 2
    key_expr_list = generate_key_expr_list(pos, I, Dist, F, alloc_matrix)
    update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, node_id = nodeID)
    post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
    key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
                                update_field_val_l = update_field_val_l, 
                                post_node_pos = post_pos, Lookahead=Lookahead, I = I, s = s)
    
    # State transition
    key_val_list = key_val_list
    tran_idx_list = tran_idx_list
    default_idx_node = default_idx_node
    # Build the state transition logic with a for loop
    ret_idx = generate_return_idx(key_val_list, tran_idx_list, 
                                  default_idx_node, num_transitions, size_of_key, key_sel,
                                  idx, node_id = nodeID)
    
    return update_field_val_l, post_pos, ret_idx
# Should be OK
def node3(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, tran_idx_list, default_idx_node, s):
    nodeID = 3
    key_expr_list = generate_key_expr_list(pos, I, Dist, F, alloc_matrix)
    update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, node_id = nodeID)
    post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
    key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
                                update_field_val_l = update_field_val_l, 
                                post_node_pos = post_pos, Lookahead=Lookahead, I = I, s = s)
    
    # State transition
    key_val_list = key_val_list
    tran_idx_list = tran_idx_list
    default_idx_node = default_idx_node
    # Build the state transition logic with a for loop
    ret_idx = generate_return_idx(key_val_list, tran_idx_list, 
                                  default_idx_node, num_transitions, size_of_key, key_sel,
                                  idx, node_id = nodeID)
    
    return update_field_val_l, post_pos, ret_idx

# Function to generate temporary BitVec variables for each iteration
# DONE
def temporary_bitvec_for_counterexample(I_val, random_initial_value_list):
    # Dynamically create new BitVec variable for this iteration
    Input_bitstream = BitVec(f'Input_bitstream_{I_val}', 14)  # 8-bit for example, can be adjusted
    input_field0 = BitVec(f'input_field0_{I_val}', 8)
    input_field1 = BitVec(f'input_field1_{I_val}', 4)
    input_field2 = BitVec(f'input_field2_{I_val}', 6)
    
    # Define constraints for this temporary BitVec based on the counterexample
    constraint = []
    constraint.append(Input_bitstream == I_val)  # Constraint depends on the counterexample
    constraint.append(input_field0 == random_initial_value_list[0])
    constraint.append(input_field1 == random_initial_value_list[1])
    constraint.append(input_field2 == random_initial_value_list[2])
    
    return Input_bitstream, [input_field0, input_field1, input_field2], constraint
# Should be OK
def implementation(Flags, Input_bitstream, idx, pos, random_initial_value_list, 
                   alloc_matrix, Lookahead, 
                   key_val_2D_list, tran_idx_2D_list, default_idx_node_list, s):
    
    Input_bitstream, Input_Fields, temp_constraint = temporary_bitvec_for_counterexample(Input_bitstream, random_initial_value_list)
    s.add(temp_constraint)

    # Input_Fields = [input_field0, input_field1]
    Out_Fields, post_pos, idx_after_node0 = node0(Flags[0], Input_Fields, Input_bitstream, 
                                    idx=idx, pos=pos, alloc_matrix=alloc_matrix, Lookahead=Lookahead, 
                                    key_val_list=key_val_2D_list[0], tran_idx_list=tran_idx_2D_list[0], 
                       default_idx_node=default_idx_node_list[0],s=s)
    Out_Fields, post_pos, idx_after_node1 = node1(Flags[1], Out_Fields, Input_bitstream, 
                       idx=idx_after_node0, pos=post_pos, alloc_matrix=alloc_matrix, Lookahead=Lookahead, 
                       key_val_list=key_val_2D_list[1], tran_idx_list=tran_idx_2D_list[1], 
                       default_idx_node=default_idx_node_list[1],s=s)
    Out_Fields, post_pos, idx_after_node2 = node2(Flags[2], Out_Fields, Input_bitstream, 
                       idx=idx_after_node1, pos=post_pos, alloc_matrix=alloc_matrix, Lookahead=Lookahead, 
                       key_val_list=key_val_2D_list[2], tran_idx_list=tran_idx_2D_list[2], 
                       default_idx_node=default_idx_node_list[2],s=s)
    Out_Fields, post_pos, idx_after_node3 = node3(Flags[3], Out_Fields, Input_bitstream, 
                       idx=idx_after_node2, pos=post_pos, alloc_matrix=alloc_matrix, Lookahead=Lookahead, 
                       key_val_list=key_val_2D_list[3], tran_idx_list=tran_idx_2D_list[3], 
                       default_idx_node=default_idx_node_list[3], s=s)
    return Out_Fields

# Input_bitstream is a bitVec var in z3
# TODO: should generate the specification automatically
# DONE
def specification(Input_bitstream, initial_field_val_list):
    # out_field1 = BitVec(f'out_field0_{I_val}', 4)
    O_field0 = Extract(13, 13 - 8 + 1, Input_bitstream)
    idx0 = 1
    idx1 = If(Extract(3, 0, O_field0) == BitVecVal(0b1111, 4), 1, 0)
    O_field1 = If(idx1 == 1, Extract(5, 2, Input_bitstream), initial_field_val_list[1])
    idx2 = If(Extract(3, 0, O_field0) == BitVecVal(0b0011, 4), 1, 0)
    O_field2 = If(idx2 == 1, Extract(5, 0, Input_bitstream), initial_field_val_list[2])
    
    return [O_field0, O_field1, O_field2], [idx0, idx1, idx2]

# DONE
def spec(Input_bitstream, initial_list):
    # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
    Fields = ["", "", ""]
    Fields[0] = Input_bitstream[0 : 8]
    if Fields[0][4 : 8] == "1111":
        Fields[1] = Input_bitstream[8 : 8 + 4]
    elif Fields[0][4 : 8] == "0011":
        Fields[2] = Input_bitstream[8 : 8 + 6]
    l = []
    for i in range(len(Fields)):
        if Fields[i] != "":
            l.append(int(Fields[i], 2))
        else:
            l.append(initial_list[i])
    return l

# DONE
def flag_gen(num_parser_nodes, num_pkt_fields):
    Flags = []
    # Define the flags using nested loops
    for i in range(num_parser_nodes):  # Loop over flag groups (Flags[0], Flags[1], Flags[2], Flag3)
        flag_row = []  # List to hold each row of flags (e.g., Flag0 = [flag_0_0, flag_0_1, flag_0_2])
        for j in range(num_pkt_fields):  # Loop to define each flag in a row (flag_0_0, flag_0_1, etc.)
            flag_row.append(Int(f'flag_{i}_{j}'))  # Dynamically create variable names
        Flags.append(flag_row)  # Append the row to the Flags list

    return Flags

#DONE
def alloc_matrix_gen(pkt_field_size_list):
    alloc_matrix = []
    # Loop to define the variables and populate the matrix
    for i in range(len(pkt_field_size_list)):  # Loop over the rows
        row = []  # Initialize an empty list for the current row
        for j in range(pkt_field_size_list[i]):  # Loop over the elements in the current row
            # Create a variable with a name 'field{i}_{j}' and append it to the row
            row.append(Int(f'field{i}_{j}'))
        # Append the row to the alloc_matrix
        alloc_matrix.append(row)
    return alloc_matrix
#DONE
def lookahead_gen(num_parser_nodes, lookahead_window_size):
    Lookahead = []
    # Define the Lookahead variables using nested loops
    for i in range(num_parser_nodes):  # Loop over 4 nodes (node0, node1, node2, node3)
        node_ahead = []  # List to store the ahead variables for each node (e.g., node0_ahead0, node0_ahead1)
        for j in range(lookahead_window_size):  # Each node has two lookahead variables (ahead0 and ahead1)
            node_ahead.append(Int(f'node{i}_ahead{j}'))  # Dynamically create variable names like node0_ahead0
        Lookahead.append(node_ahead)  # Append the node lookahead list to Lookahead
    return Lookahead

def key_val_gen(num_transitions, size_of_key, num_parser_nodes):
    key_val_2D_list = []
    for nodeID in range(num_parser_nodes):
        row = [BitVec(f'key_val{i}_node{nodeID}', size_of_key) for i in range(num_transitions)]
        key_val_2D_list.append(row)
    return key_val_2D_list

def tran_idx_gen(num_transitions, num_parser_nodes):
    tran_idx_2D_list = []
    for nodeID in range(num_parser_nodes):
        row=[Int(f'tran_idx{i}_node{nodeID}') for i in range(num_transitions)]
        tran_idx_2D_list.append(row)
    return tran_idx_2D_list

def default_idx_gen(num_parser_nodes):
    default_idx_node_list = []
    for nodeID in range(num_parser_nodes):
        default_idx_node_list.append(Int(f'default_idx_node{nodeID}'))
    return default_idx_node_list

def synthesis_step(cexamples):
    print("Enter synthsis phase")
    # Define all variables
    # Create a solver to synthesize f(x)
    s = Solver()
    s.reset()

    Flags = flag_gen(num_parser_nodes=num_parser_nodes, num_pkt_fields=num_pkt_fields)    
    # Define the constraints
    for j in range(num_pkt_fields):  # Loop over each column (flag_0_0, flag_1_0, etc.)
        # s.add(Flags[0][j] + Flags[1][j] + Flags[2][j] + Flags[3][j] <= 1)  # Column constraints
        s.add(Sum([Flags[i][j] for i in range(num_parser_nodes)]) <= 1)

    # Add constraints for the sum of each row (Flag0, Flag1, etc.)
    for i in range(num_parser_nodes):  # Loop over each Flag row
        s.add(Sum(Flags[i]) <= 1)

    # Add constraints for each element being 0 or 1
    for i in range(num_parser_nodes):
        for j in range(num_pkt_fields):
            s.add(Or(Flags[i][j] == 0, Flags[i][j] == 1))

    idx = Int('idx')
    s.add(idx == 0)
    pos = Int('pos')
    s.add(pos == 0)

    # Initialize an empty list to hold the matrix
    alloc_matrix = alloc_matrix_gen(pkt_field_size_list=pkt_field_size_list)
    
    # Create an empty list to store Lookahead nodes
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)
    
    key_val_2D_list = key_val_gen(num_transitions=num_transitions, size_of_key=size_of_key, 
                                  num_parser_nodes=num_parser_nodes)
    tran_idx_2D_list = tran_idx_gen(num_transitions=num_transitions,num_parser_nodes=num_parser_nodes)
    
    default_idx_node_list = default_idx_gen(num_parser_nodes=num_parser_nodes)

    if not cexamples:
        # If no counterexamples exist yet, try to find any function
        print("Counterexample set cannot be empty")
        sys.exit(1)
    else:
        for Input_bitval in cexamples:
            # input bit stream I = [0,0,0,0,...0]
            # Out_spec = spec(I)
            # Out_impl = impl(I, initial_val_of_input_fields)
            # Generate several random initial values
            random_initial_value_list = []
            for i in range(num_pkt_fields):
                random_initial_value_list.append(random.randint(0, 2**pkt_field_size_list[i] - 1))
            impl_out = implementation(Flags, Input_bitval, idx, pos, random_initial_value_list, 
                                      alloc_matrix, Lookahead, 
                                      key_val_2D_list=key_val_2D_list, 
                                      tran_idx_2D_list=tran_idx_2D_list, 
                                      default_idx_node_list=default_idx_node_list, s=s)
            spec_out = spec(format(Input_bitval, '014b'), random_initial_value_list)
            for i in range(len(impl_out)):
                s.add(impl_out[i] == spec_out[i])

    # Check if the constraints are satisfiable
    if s.check() == sat:
        model = s.model()
        return model # return synthesis result
    else:
        # No valid solution found for current counterexamples
        print("No solution found for the given counterexamples.")
        return None

def verification_step(model, cexamples):
    print("Enter verification phase")
    # Try to find a counterexample where f(x) != g(x)
    x = BitVec('x', input_bit_stream_size)
    s = Solver()

    # Constraint: f(x) = coeff * x + bias should equal g(x) = x + 1
    Flags = flag_gen(num_parser_nodes=num_parser_nodes, num_pkt_fields=num_pkt_fields)    
    # Initialize an empty list to hold the matrix
    alloc_matrix = alloc_matrix_gen(pkt_field_size_list=pkt_field_size_list)
    # Create an empty list to store Lookahead nodes
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)

    for i in range(len(Flags)):
        for j in range(len(Flags[i])):
            value = model.evaluate(Flags[i][j], model_completion=True)
            if value is not None:
                s.add(Flags[i][j] == value.as_long())
            else:
                s.add(Flags[i][j] == 0)
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i])):
            value = model.evaluate(alloc_matrix[i][j], model_completion=True)
            if value is not None:
                s.add(alloc_matrix[i][j] == value.as_long())
            else:
                s.add(alloc_matrix[i][j] == -1)
    for i in range(len(Lookahead)):
        for j in range(len(Lookahead[i])):
            value = model.evaluate(Lookahead[i][j], model_completion=True)
            if value is not None:
                s.add(Lookahead[i][j] == value.as_long())
            else:
                s.add(Lookahead[i][j] == 0)
    
    key_val_2D_list = key_val_gen(num_transitions=num_transitions, size_of_key=size_of_key, 
                                  num_parser_nodes=num_parser_nodes)
    for i in range(len(key_val_2D_list)):
        for j in range(len(key_val_2D_list[i])):
            value = model.evaluate(key_val_2D_list[i][j], model_completion=True)
            if value is not None:
                s.add(key_val_2D_list[i][j] == value.as_long())
            else:
                s.add(key_val_2D_list[i][j] == 0)
    tran_idx_2D_list = tran_idx_gen(num_transitions=num_transitions,num_parser_nodes=num_parser_nodes)
    for i in range(len(tran_idx_2D_list)):
        for j in range(len(tran_idx_2D_list[i])):
            value = model.evaluate(tran_idx_2D_list[i][j], model_completion=True)
            if value is not None:
                s.add(tran_idx_2D_list[i][j] == value.as_long())
            else:
                s.add(tran_idx_2D_list[i][j] == num_parser_nodes + 1)

    default_idx_node_list = default_idx_gen(num_parser_nodes=num_parser_nodes)
    for i in range(len(default_idx_node_list)):
        value = model.evaluate(default_idx_node_list[i], model_completion=True)
        if value is not None:
            s.add(default_idx_node_list[i] == value.as_long())
        else:
            s.add(default_idx_node_list[i] == num_parser_nodes + 1)

    idx = Int('idx')
    s.add(idx == 0)
    pos = Int('pos')
    s.add(pos == 0)
    # TODO: sometimes, these initial values may affect the final outcome
    initial_field_value_l = []
    for i in range(num_pkt_fields):
        initial_field_value_l.append(random.randint(0, 2**pkt_field_size_list[i] - 1))
    O_Impl = implementation(Flags=Flags, Input_bitstream=x, idx=idx, pos=pos, 
                            random_initial_value_list=initial_field_value_l,
                             alloc_matrix=alloc_matrix, Lookahead=Lookahead, 
                             key_val_2D_list=key_val_2D_list, tran_idx_2D_list=tran_idx_2D_list, 
                             default_idx_node_list=default_idx_node_list, s=s)
    O_Spec, Modify_idx = specification(x, initial_field_value_l)

    constraints = []
    for i in range(num_pkt_fields):  # You can generalize this range based on your list size
        constraints.append(And(O_Impl[i] != O_Spec[i], Modify_idx[i] == 1))
    s.add(Or(constraints))
    for i in range(len(cexamples)):
        s.add(x != cexamples[i])

    if s.check() == sat:
        model = s.model()
        return model[x].as_long()  # Return the counterexample value for x
    else:
        return None  # No counterexample found, the candidate function is valid


def cegis_loop():
    cexamples = [0] # Start with one counterexamples  
    maxIter = 100# Alternatively, we can set it to be # input space.
    for i in range(maxIter):
        print("cexamples =", sorted(cexamples), "# cex =", len(cexamples))
        # Synthesis step: generate a new candidate solution f(x)
        candidate = synthesis_step(cexamples)
        if candidate is None:
            print("Synthesis failed, no valid function found.")
            return
        
        # codegen the result
        # Create a dictionary to store the model's output
        model_dict = {}
        
        # Extract each variable and its corresponding value
        for d in candidate:
            model_dict[d.name()] = candidate[d].as_long()  # Convert Z3 values to Python values

        # Convert the dictionary to JSON
        model_json = json.dumps(model_dict)
        p4_in_json = codegen(model_json, number_of_parser_nodes=num_parser_nodes, size_of_key=size_of_key)

        cexample = verification_step(model=candidate, cexamples=cexamples)
        if cexample is None:
            print(f"Valid function found")
            return
        else:
            print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round

# Run the CEGIS loop
cegis_loop()