from z3 import *

from bitarray import bitarray
import random
import sys
import json
import random

import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))
# Now you can import the library from Folder B
from practical_ex.code_gen_IPU import *

"""
spec:
state ethernet {
    b.extract(hdr.data);  --> 48-bit
    transition select(hdr.data.f33) {
        1: parse_llc_header;
        0: parse_llc_header;
        default: accept;
    }
}
state parse_llc_header {
    b.extract(hdr.data1); --> 24-bit
    transition accept;
}
"""

synthesis_time = 0
verification_time = 0
total_iterations = 0
has_run = False  # global guard
search_space_bit = 0

input_bit_stream_size = 1 + 16 + 1

pkt_field_size_list = [1, 16, 1, 1, 1]
key_field_list = [0, 16, 0, 0, 0]
num_pkt_fields = len(pkt_field_size_list)

# List the hardware configuration
lookahead_window_size = 0
size_of_key = 16
num_parser_nodes = 5

parser_node_pipe = [1,1,3]
num_parser_nodes = sum(parser_node_pipe)
tcam_num = 3

# TODO: should generate the specification automatically
# Input: Input_bitstream with the type bitVec var in z3, and initial value of all fields
# Output: Updated value of all packet fields
def specification(Input_bitstream, initial_field_val_list):
    # out_field1 = BitVec(f'out_field0_{I_val}', 4)
    #      1   1  1  1 0 0 0 0 1 1 1 0 0 0
    #  pos 0   1  2  3 4
    #  idx 13 12 11 10 9 8 
    O_field0 = Extract(input_bit_stream_size - 1, input_bit_stream_size - 1 - pkt_field_size_list[0] + 1, Input_bitstream) #node 0
    O_field1 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] + 1, Input_bitstream)
    pos_beg = input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1]
    Cond1 = Extract(15, 0, O_field1) == BitVecVal(0x0800, 16)
    Cond2 = Extract(15, 0, O_field1) == BitVecVal(0x86dd, 16)
    Cond3 = Extract(15, 0, O_field1) == BitVecVal(0x0806, 16)
    O_field2 = If(Cond1, Extract(pos_beg, pos_beg  - pkt_field_size_list[2] + 1, Input_bitstream), initial_field_val_list[2])
    O_field3 = If(Cond2, Extract(pos_beg, pos_beg  - pkt_field_size_list[3] + 1, Input_bitstream), initial_field_val_list[3])
    O_field4 = If(Cond3, Extract(pos_beg, pos_beg  - pkt_field_size_list[4] + 1, Input_bitstream), initial_field_val_list[4])

    return [O_field0, O_field1, O_field2, O_field3, O_field4]

# TODO: should generate the spec automatically
# Input: Input_bitstream with the type string, and initial value of all fields
# Output: updated fields' value in int type
def spec(Input_bitstream, initial_list):
    # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
    Fields = ["" for _ in range(num_pkt_fields)]
    Fields[0] = Input_bitstream[0 : pkt_field_size_list[0]]
    Fields[1] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[1]]
    curr_pos = pkt_field_size_list[0] + pkt_field_size_list[1]
    if int(Fields[1][0 : 16], 2) == 0x0800:
        Fields[2] = Input_bitstream[curr_pos : curr_pos + pkt_field_size_list[2]]
    elif int(Fields[1][0 : 16], 2) == 0x86dd:
        Fields[3] = Input_bitstream[curr_pos : curr_pos + pkt_field_size_list[3]]
    elif int(Fields[1][0 : 16], 2) == 0x0806:
        Fields[4] = Input_bitstream[curr_pos : curr_pos + pkt_field_size_list[4]]
    l = []
    for i in range(num_pkt_fields):
        if Fields[i] != "":
            l.append(int(Fields[i], 2))
        else:
            l.append(initial_list[i])
    return l

# Automaticall generate the nested ITE statement in z3
# e.g.,
# If(And(Dist[0] == 1, pos == 0), Extract(13, 6, I),
#                         If(And(Dist[0] == 1, pos == 1), Extract(12, 5, I),
#                         If(And(Dist[0] == 1, pos == 2), Extract(11, 4, I),
#                         ...
#                         If(And(Dist[0] == 1, pos == 6), Extract(7, 0, I),
#                                 F[0])))))))
def dynamic_extract_loop(s, pos, I, Dist, F, field_size, field_id):
    expr = F
    for i in range(input_bit_stream_size - field_size + 1):
        start = input_bit_stream_size - 1 - i
        end = start - (field_size - 1)
        if end < 0:
            break
        # Construct the If expression with And conditions
        expr = If(And(Dist[field_id] == 1, pos == i), Extract(start, end, I), expr)
    return expr

def generate_key_expr_list(s, pos, I, Dist, F, alloc_matrix):
    ret_l = []
    for i in range(len(alloc_matrix)):
        ret_l.append(dynamic_extract_loop(s, pos, I, Dist, F[i], len(alloc_matrix[i]), field_id=i))
    return ret_l

def generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id):
    ret_l = []
    for i in range(len(alloc_matrix)):
        # s.add(Implies(Dist[i] == 1, key_expr_list[i] != None))
        ret_l.append(If(And(idx == node_id, Dist[i] == 1), key_expr_list[i], F[i]))
    return ret_l

def generate_tran_key(alloc_matrix, node_id, update_field_val_l, 
                      post_node_pos, Lookahead, I, s):
    dummy = BitVec('dummy', 1)
    s.add(dummy == 0)
    key_sel = None
    # Only extracted fields can be used as the state transition key
    # for i in range(len(alloc_matrix)):
    #     for j in range(len(alloc_matrix[i])):
    #         s.add(Implies(alloc_matrix[i][j] == node_id, extract_status[i] == 1))

    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i]) - 1, -1, -1):
            if key_sel == None:
                key_sel = If(alloc_matrix[i][j] == node_id, Extract(j,j,update_field_val_l[i]),dummy)    
            else:
                key_sel = If(alloc_matrix[i][j] == node_id, Concat(key_sel, Extract(j,j,update_field_val_l[i])), Concat(dummy, key_sel))    
    
    for j in range(lookahead_window_size):
        for i in range(input_bit_stream_size):
            if input_bit_stream_size - 1 - i - j < 0:
                break
            key_sel = If(And(Lookahead[node_id][j] == 1, post_node_pos == i), Concat(key_sel, Extract(input_bit_stream_size - 1 - i - j, input_bit_stream_size - 1 - i - j, I)), Concat(dummy, key_sel))
    return key_sel

def post_node_pos(idx, Dist, node_id, alloc_matrix, pos):
    # Start with the base case: if none of Dist[i] == 1 apply, return pos
    result = pos
    
    # Loop over the indices and build the nested If conditions
    for i in range(len(Dist) - 1, -1, -1):  # Reverse order to build nested If from the inside out
        result = If(Dist[i] == 1, pos + len(alloc_matrix[i]), result)
    
    # Add the outermost condition for idx
    return If(idx == node_id, result, pos)

# def generate_return_idx(key_val_list, key_mask_list, tran_idx_list, default_idx_node1, num_transitions, size_of_key, key_sel, idx, node_id):
def generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node1, size_of_key, key_sel, idx, node_id):
    ret_idx = default_idx_node1  # Default case
    # Reverse the order because we want to make the TCAM entry with smaller number to dominate the transition logic
    for i in range(tcam_num - 1, -1, -1):
        # key_val_list = BitVec(name, size_of_key);
        ret_idx = If(And(assignments[i] == node_id, (Extract(size_of_key - 1, 0, key_sel) & key_mask_total_list[i]) == (key_val_total_list[i] & key_mask_total_list[i])), tran_idx_total_list[i], ret_idx)

    # Final state transition for idx == 1
    ret_idx = If(idx == node_id, ret_idx, idx)
    return ret_idx

def new_node(nodeID, Dist, F, I, idx, pos, alloc_matrix, Lookahead, assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node, s):
    key_expr_list = generate_key_expr_list(s, pos, I, Dist, F, alloc_matrix)
    update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id = nodeID)
    post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
    key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
                                update_field_val_l = update_field_val_l, 
                                post_node_pos = post_pos, Lookahead=Lookahead, I = I, s = s)
    
    # State transition
    # key_val_list = key_val_list
    # tran_idx_list = tran_idx_list
    # default_idx_node = default_idx_node
    # Build the state transition logic with a for loop
    ret_idx = generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, 
                                  default_idx_node, size_of_key, key_sel,
                                  idx, node_id = nodeID)
    
    return update_field_val_l, post_pos, ret_idx
# # Behavior of parser node 1
# # def node1(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, key_mask_list, tran_idx_list, default_idx_node, extract_status, s):
# def node1(Dist, F, I, idx, pos, alloc_matrix, Lookahead, assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node, extract_status, s):
#     nodeID = 1
#     # for i in range(num_pkt_fields):
#     #     s.add(Implies(And(Dist[i] == 1, idx == nodeID), pos + pkt_field_size_list[i] < input_bit_stream_size))
#     key_expr_list = generate_key_expr_list(s, pos, I, Dist, F, alloc_matrix)
#     update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id = nodeID)
#     post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
#     extract_status = update_extract_states(idx = idx, Dist=Dist, extract_status=extract_status, 
#                                                 node_id=nodeID, num_pkt_fields=num_pkt_fields)
#     key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
#                                 update_field_val_l = update_field_val_l, 
#                                 post_node_pos = post_pos, Lookahead=Lookahead, I = I, extract_status=extract_status, s = s)
    
#     # State transition
#     # key_val_list = key_val_list
#     # tran_idx_list = tran_idx_list
#     # default_idx_node = default_idx_node
#     # Build the state transition logic with a for loop
#     ret_idx = generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list,  
#                                   default_idx_node, size_of_key, key_sel,
#                                   idx, node_id = nodeID)
    
#     return update_field_val_l, post_pos, ret_idx, extract_status

# # Behavior of parser node 2
# # def node2(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, key_mask_list, tran_idx_list, default_idx_node, extract_status, s):
# def node2(Dist, F, I, idx, pos, alloc_matrix, Lookahead, assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node, extract_status, s):
#     nodeID = 2
#     # for i in range(num_pkt_fields):
#     #     s.add(Implies(And(Dist[i] == 1, idx == nodeID), pos + pkt_field_size_list[i] < input_bit_stream_size))
#     key_expr_list = generate_key_expr_list(s, pos, I, Dist, F, alloc_matrix)
#     update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id = nodeID)
#     post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
#     extract_status = update_extract_states(idx = idx, Dist=Dist, extract_status=extract_status, 
#                                                 node_id=nodeID, num_pkt_fields=num_pkt_fields)
#     key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
#                                 update_field_val_l = update_field_val_l, 
#                                 post_node_pos = post_pos, Lookahead=Lookahead, I = I, extract_status=extract_status, s = s)
    
#     # State transition
#     # key_val_list = key_val_list
#     # tran_idx_list = tran_idx_list
#     # default_idx_node = default_idx_node
#     # Build the state transition logic with a for loop
#     ret_idx = generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, 
#                                   default_idx_node, size_of_key, key_sel,
#                                   idx, node_id = nodeID)
    
#     return update_field_val_l, post_pos, ret_idx, extract_status

# # Behavior of parser node 3
# # def node3(Dist, F, I, idx, pos, alloc_matrix, Lookahead, key_val_list, key_mask_list, tran_idx_list, default_idx_node, extract_status, s):
# def node3(Dist, F, I, idx, pos, alloc_matrix, Lookahead, assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node, extract_status, s):
#     nodeID = 3
#     # for i in range(num_pkt_fields):
#     #     s.add(Implies(And(Dist[i] == 1, idx == nodeID), pos + pkt_field_size_list[i] < input_bit_stream_size))
#     key_expr_list = generate_key_expr_list(s, pos, I, Dist, F, alloc_matrix)
#     update_field_val_l = generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id = nodeID)
#     post_pos = post_node_pos(idx = idx, Dist = Dist, node_id = nodeID, alloc_matrix=alloc_matrix, pos = pos)
#     extract_status = update_extract_states(idx = idx, Dist=Dist, extract_status=extract_status, 
#                                                 node_id=nodeID, num_pkt_fields=num_pkt_fields)
#     key_sel = generate_tran_key(alloc_matrix = alloc_matrix, node_id = nodeID, 
#                                 update_field_val_l = update_field_val_l, 
#                                 post_node_pos = post_pos, Lookahead=Lookahead, I = I, extract_status=extract_status, s = s)
    
#     # State transition
#     # key_val_list = key_val_list
#     # tran_idx_list = tran_idx_list
#     # default_idx_node = default_idx_node
#     # Build the state transition logic with a for loop
#     ret_idx = generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, 
#                                   default_idx_node, size_of_key, key_sel,
#                                   idx, node_id = nodeID)
    
#     return update_field_val_l, post_pos, ret_idx, extract_status

# Function to generate temporary BitVec variables for each iteration
def temporary_bitvec_for_counterexample(I_val, random_initial_value_list, num_pkt_fields, testcaseID):
    # Dynamically create new BitVec variable for this iteration
    Input_bitstream = BitVec(f'Input_bitstream_{testcaseID}', input_bit_stream_size)  # 8-bit for example, can be adjusted
    input_fields = []
    for i in range(len(pkt_field_size_list)):  # Change to desired number of fields, e.g., 3 for input_field0 to input_field2
        bv = BitVec(f'input_field{i}_{testcaseID}', pkt_field_size_list[i])
        input_fields.append(bv)
    
    # Define constraints for this temporary BitVec based on the counterexample
    constraint = []
    constraint.append(Input_bitstream == I_val)  # Constraint depends on the counterexample
    for i in range(len(pkt_field_size_list)):  # Change to desired number of fields, e.g., 3 for input_field0 to input_field2
        constraint.append(input_fields[i] == random_initial_value_list[i])

    # return Input_bitstream, [input_field0, input_field1, input_field2], extract_status, constraint
    return Input_bitstream, input_fields, constraint

# Implementation, concrete z3 variables' values are decided by the z3 solver
def implementation(Flags, Input_bitstream, idx, pos, random_initial_value_list, 
                   alloc_matrix, Lookahead, 
                   assignments,
                #    key_val_2D_list, key_mask_2D_list, tran_idx_2D_list, 
                   key_val_total_list, key_mask_total_list, tran_idx_total_list,
                   default_idx_node_list, testcaseID, 
                   s):
    
    Input_bitstream, Input_Fields, temp_constraint = temporary_bitvec_for_counterexample(I_val=Input_bitstream, 
                                                                                                         random_initial_value_list=random_initial_value_list, 
                                                                                                         num_pkt_fields=num_pkt_fields, testcaseID=testcaseID)
    s.add(temp_constraint)

    # Using for loop to replace the iterative accessing the node function
    # nodes = [] # list of function names
    # for i in range(num_parser_nodes):
        # node_function = globals()[f'node{i}']  # Access the function dynamically by its name
        # nodes.append(node_function)
    Out_Fields = Input_Fields
    post_pos = pos

    sum_l = []
    for v in parser_node_pipe:
        if len(sum_l) == 0:
            sum_l.append(v)
        else:
            sum_l.append(sum_l[-1] + v)
    for i in range(num_parser_nodes):
        if i == 0:
            Out_Fields, post_pos, idx = new_node(0, Flags[0], Out_Fields, Input_bitstream, 
                                                                        idx=idx, pos=post_pos, alloc_matrix=alloc_matrix, 
                                                                        Lookahead=Lookahead, 
                                                                        # key_val_list=key_val_2D_list[0], 
                                                                        # key_mask_list=key_mask_2D_list[0], 
                                                                        # tran_idx_list=tran_idx_2D_list[0],
                                                                        assignments=assignments[0],
                                                                        key_val_total_list=key_val_total_list[0], 
                                                                        key_mask_total_list=key_mask_total_list[0], 
                                                                        tran_idx_total_list=tran_idx_total_list[0],
                                                                        default_idx_node=default_idx_node_list[0], 
                                                                        s=s)
        else:
            assign_id = 0
            curr_sum = 0
            for j in range(len(parser_node_pipe)):
                curr_sum += parser_node_pipe[j]
                if curr_sum > i:
                    assign_id = j
                    break
            Out_Fields, post_pos, idx = new_node(i, 
                Flags[i], Out_Fields, Input_bitstream, idx=idx, pos=post_pos, alloc_matrix=alloc_matrix,
                Lookahead=Lookahead, 
                # key_val_list=key_val_2D_list[i], key_mask_list=key_mask_2D_list[i], tran_idx_list=tran_idx_2D_list[i],
                assignments=assignments[assign_id],
                key_val_total_list=key_val_total_list[assign_id],
                key_mask_total_list=key_mask_total_list[assign_id], 
                tran_idx_total_list=tran_idx_total_list[assign_id],
                default_idx_node=default_idx_node_list[i], s=s
            )
    return Out_Fields

# Generate Flag variables
# e.g.
#    flag_0_0 = Int('flag_0_0')
#    flag_0_1 = Int('flag_0_1')
#    ... 
#    flag_3_1 = Int('flag_3_1')
#    flag_3_2 = Int('flag_3_2')
def flag_gen(num_parser_nodes, num_pkt_fields):
    Flags = []
    # Define the flags using nested loops
    for i in range(num_parser_nodes):  
        flag_row = []  
        for j in range(num_pkt_fields):  
            flag_row.append(Int(f'flag_{i}_{j}'))  # Dynamically create variable names
        Flags.append(flag_row)  # Append the row to the Flags list

    return Flags

# Generate alloc_matrix variables
# e.g.,
# field0_0 = Int('field0_0')
# field0_1 = Int('field0_1')
# ...
# field2_4 = Int('field2_4')
# field2_5 = Int('field2_5')
# alloc_matrix = [[field0_0, field0_1, field0_2, field0_3, field0_4, field0_5, field0_6, field0_7], 
#                 [field1_0, field1_1, field1_2, field1_3], 
#                 [field2_0, field2_1, field2_2, field2_3, field2_4, field2_5]]
def alloc_matrix_gen(pkt_field_size_list):
    alloc_matrix = []
    # Loop to define the variables and populate the matrix
    for i in range(len(pkt_field_size_list)):  
        row = []  
        for j in range(pkt_field_size_list[i]):
            # Create a variable with a name 'field{i}_{j}' and append it to the row
            row.append(Int(f'field{i}_{j}'))
        alloc_matrix.append(row)
    return alloc_matrix

# Generate loop ahead variables (similar to alloc_matrix)
def lookahead_gen(num_parser_nodes, lookahead_window_size):
    Lookahead = []
    for i in range(num_parser_nodes):  
        node_ahead = []  
        for j in range(lookahead_window_size): 
            node_ahead.append(Int(f'node{i}_ahead{j}'))  # Dynamically create variable names like node0_ahead0
        Lookahead.append(node_ahead)  # Append the node lookahead list to Lookahead
    return Lookahead

def assignment_gen(stage_num, tcam_num):
    assignments = []
    for i in range(stage_num):
        assign = []
        for j in range(tcam_num):
            assign.append(Int(f'assign_stage_{j}_tcam{i}'))
        assignments.append(assign)
    return assignments

def key_val_gen(stage_num, tcam_num):
    key_val_total_list = []
    for i in range(stage_num):
        key_val_l = []
        for j in range(tcam_num):
            key_val_l.append(BitVec(f'key_val_stage_{j}_tcam{i}',size_of_key))
        key_val_total_list.append(key_val_l)
    return key_val_total_list

def key_mask_gen(stage_num, tcam_num):
    key_mask_total_list = []
    for i in range(stage_num):
        key_mask_l = []
        for j in range(tcam_num):
            key_mask_l.append(BitVec(f'key_mask_stage_{j}_tcam{i}',size_of_key))
        key_mask_total_list.append(key_mask_l)
    return key_mask_total_list

def tran_id_gen(stage_num, tcam_num):
    tran_idx_total_list = []
    for i in range(stage_num):
        tran_idx_l = []
        for j in range(tcam_num):
            tran_idx_l.append(Int(f'tran_idx_stage_{j}_tcam{i}'))
        tran_idx_total_list.append(tran_idx_l)
    return tran_idx_total_list

# Generate default transition index in each parser node
# e.g., default_idx_node0 = Int('default_idx_node0')
def default_idx_gen(num_parser_nodes):
    default_idx_node_list = []
    for i in range(num_parser_nodes):
        default_idx_node_list.append(Int(f'default_idx_node_{i}'))
    return default_idx_node_list

def synthesis_step(cexamples):
    print("Enter synthsis phase")
    global has_run
    global search_space_bit
    # Define all variables
    s = Solver()
    s.reset()
    # s.set("incremental", True)


    Flags = flag_gen(num_parser_nodes=num_parser_nodes, num_pkt_fields=num_pkt_fields)    
    # Define the constraints
    for j in range(num_pkt_fields):  
        # s.add(Flags[0][j] + Flags[1][j] + Flags[2][j] + Flags[3][j] <= 1)  # Column constraints
        s.add(Sum([Flags[i][j] for i in range(num_parser_nodes)]) <= 1)

    # Add constraints for the sum of each row 
    for i in range(num_parser_nodes):
        # e.g., s.add(Sum(Flag[0]) <= 1)
        s.add(Sum(Flags[i]) <= 1)

    # Add constraints for each element being 0 or 1
    for i in range(num_parser_nodes):
        for j in range(num_pkt_fields):
            s.add(Or(Flags[i][j] == 0, Flags[i][j] == 1))

    idx = Int('idx')
    s.add(idx == 0)
    pos = Int('pos')
    s.add(pos == 0)

    alloc_matrix = alloc_matrix_gen(pkt_field_size_list=pkt_field_size_list)
    
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)
    
    # key_val_2D_list, key_mask_2D_list = key_val_gen(num_transitions=num_transitions, size_of_key=size_of_key, 
    #                               num_parser_nodes=num_parser_nodes)
    # tran_idx_2D_list = tran_idx_gen(num_transitions=num_transitions,num_parser_nodes=num_parser_nodes)
    
    default_idx_node_list = default_idx_gen(num_parser_nodes=num_parser_nodes)

    # NEW CODE
    assignments = assignment_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    # print("assignments =", assignments)
    key_val_total_list = key_val_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    key_mask_total_list = key_mask_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    tran_idx_total_list = tran_id_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    # print("key_val_total_list =", key_val_total_list)
    # print("key_mask_total_list =", key_mask_total_list)
    # print("tran_idx_total_list =", tran_idx_total_list)

    # TODO: set parser node stage by stage
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i]) - 1):
            s.add(alloc_matrix[i][j] == alloc_matrix[i][j + 1])
    for i in range(len(parser_node_pipe)):
        for j in range(tcam_num):
            s.add(key_mask_total_list[i][j] == 0xFFFF)
            s.add(Or(key_val_total_list[i][j] == 0x0800, key_val_total_list[i][j] == 0x86dd, key_val_total_list[i][j] == 0x0806))
    
    
    sum_l = []
    for v in parser_node_pipe:
        if len(sum_l) == 0:
            sum_l.append(v)
        else:
            sum_l.append(sum_l[-1] + v)
    # TODO: Add constraints to the state transition idx
    for i in range(len(parser_node_pipe)):
        for j in range(parser_node_pipe[i]):
            s.add(tran_idx_total_list[i][j] >= sum_l[i])
    # TODO: Add constraints to the default transition idx
    ID = 0
    for i in range(len(parser_node_pipe)):
        for j in range(parser_node_pipe[i]):
            s.add(default_idx_node_list[ID] >= sum_l[i])
            ID += 1

    constraints = []
    for i in range(len(parser_node_pipe)):
        for j in range(tcam_num):
            if j == 0:
                constraints.append(Or(And(assignments[i][j] >= 0, assignments[i][j] < sum_l[i]), assignments[i][j] >= num_parser_nodes))
            else:
                constraints.append(Or(And(assignments[i][j] >= sum_l[i - 1], assignments[i][j] < sum_l[i]), assignments[i][j] >= num_parser_nodes))
    s.add(constraints)

    if not cexamples:
        # We force the counterexample set to be non-empty
        print("Counterexample set cannot be empty")
        sys.exit(1)
    else:
        for j in range(len(cexamples)):
            Input_bitval = cexamples[j][0]
            random_initial_value_list = cexamples[j][1:]
            spec_out = spec(format(Input_bitval, '0{size}b'.format(size=input_bit_stream_size)), random_initial_value_list)
            impl_out = implementation(Flags, Input_bitval, idx, pos, random_initial_value_list, 
                                      alloc_matrix, Lookahead, 
                                    #   key_val_2D_list=key_val_2D_list, 
                                    #   key_mask_2D_list=key_mask_2D_list, 
                                    #   tran_idx_2D_list=tran_idx_2D_list, 
                                      assignments=assignments,
                                      key_val_total_list=key_val_total_list,
                                      key_mask_total_list=key_mask_total_list,
                                      tran_idx_total_list=tran_idx_total_list,
                                      default_idx_node_list=default_idx_node_list, 
                                      testcaseID=j,s=s)
            # the output of implementation should be equal to specification for all members in the counterexample set
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

    Flags = flag_gen(num_parser_nodes=num_parser_nodes, num_pkt_fields=num_pkt_fields)    
    alloc_matrix = alloc_matrix_gen(pkt_field_size_list=pkt_field_size_list)
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)
    # Force z3's variables to be the value output from the synthesis phase
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
    
    assignments = assignment_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    key_val_total_list = key_val_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    key_mask_total_list = key_mask_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)
    tran_idx_total_list = tran_id_gen(stage_num=len(parser_node_pipe), tcam_num=tcam_num)

    for i in range(len(assignments)):
        for j in range(len(assignments[i])):
            value = model.evaluate(assignments[i][j], model_completion=True)
            if value is not None:
                s.add(assignments[i][j] == value.as_long())
            else:
                s.add(assignments[i][j] == num_parser_nodes)
    for i in range(len(key_val_total_list)):
        for j in range(len(key_val_total_list[i])):
            value = model.evaluate(key_val_total_list[i][j], model_completion=True)
            if value is not None:
                s.add(key_val_total_list[i][j] == value.as_long())
            else:
                s.add(key_val_total_list[i][j] == -1)
    for i in range(len(key_mask_total_list)):
        for j in range(len(key_mask_total_list[i])):
            value = model.evaluate(key_mask_total_list[i][j], model_completion=True)
            if value is not None:
                s.add(key_mask_total_list[i][j] == value.as_long())
            else:
                s.add(key_mask_total_list[i][j] == -1)
    for i in range(len(tran_idx_total_list)):
        for j in range(len(tran_idx_total_list[i])):
            value = model.evaluate(tran_idx_total_list[i][j], model_completion=True)
            if value is not None:
                s.add(tran_idx_total_list[i][j] == value.as_long())
            else:
                s.add(tran_idx_total_list[i][j] == num_parser_nodes)

    # key_val_2D_list, key_mask_2D_list = key_val_gen(num_transitions=num_transitions, size_of_key=size_of_key, 
    #                               num_parser_nodes=num_parser_nodes)
    # for i in range(len(key_val_2D_list)):
    #     for j in range(len(key_val_2D_list[i])):
    #         value = model.evaluate(key_val_2D_list[i][j], model_completion=True)
    #         if value is not None:
    #             s.add(key_val_2D_list[i][j] == value.as_long())
    #         else:
    #             s.add(key_val_2D_list[i][j] == 0)
    # for i in range(len(key_mask_2D_list)):
    #     for j in range(len(key_mask_2D_list[i])):
    #         value = model.evaluate(key_mask_2D_list[i][j], model_completion=True)
    #         if value is not None:
    #             s.add(key_mask_2D_list[i][j] == value.as_long())
    #         else:
    #             s.add(key_mask_2D_list[i][j] == 0)
    # tran_idx_2D_list = tran_idx_gen(num_transitions=num_transitions,num_parser_nodes=num_parser_nodes)
    # for i in range(len(tran_idx_2D_list)):
    #     for j in range(len(tran_idx_2D_list[i])):
    #         value = model.evaluate(tran_idx_2D_list[i][j], model_completion=True)
    #         if value is not None:
    #             s.add(tran_idx_2D_list[i][j] == value.as_long())
    #         else:
    #             s.add(tran_idx_2D_list[i][j] == num_parser_nodes + 1)

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
    initial_field_value_l = []
    for i in range(num_pkt_fields):
        initial_field_value_l.append(BitVec(f'initial_field{i}', pkt_field_size_list[i]))
    O_Impl = implementation(Flags=Flags, Input_bitstream=x, idx=idx, pos=pos, 
                            random_initial_value_list=initial_field_value_l,
                             alloc_matrix=alloc_matrix, Lookahead=Lookahead,
                             assignments=assignments,
                            key_val_total_list=key_val_total_list,
                            key_mask_total_list=key_mask_total_list,
                            tran_idx_total_list=tran_idx_total_list, 
                            #  key_val_2D_list=key_val_2D_list, key_mask_2D_list=key_mask_2D_list, tran_idx_2D_list=tran_idx_2D_list, 
                             default_idx_node_list=default_idx_node_list, testcaseID=0, s=s)
    # int = 16; bitvector I should be 1 0 0 0 0 = 2**4; I[0] = 0 = 16 % 2; I[1] = 0 = 16 / 2 % 2; I[2] = 0 = 16 / 2 / 2 % 2; I[3] = 0; I[4] = 1
    # For parser, bitvector I should be 1 0 0 0 0 = 2**4; I[0] = 0 = 16 % 2; I[1] = 0 = 16 / 2 % 2; I[2] = 0 = 16 / 2 / 2 % 2; I[3] = 0; I[4] = 1
    # BitVec v = 1 0 0; Int(v) = 4;
    O_Spec = specification(x, initial_field_value_l)
    constraints = []
    for i in range(num_pkt_fields): 
        constraints.append(And(O_Impl[i] != O_Spec[i]))
    s.add(Or(constraints))

    if s.check() == sat:
        model = s.model()
        # Return counter example's value, including the input bitstream + all packet fields' initial values
        cex_ret_l = [model[x].as_long()]
        for i in range(num_pkt_fields):
            cex_ret_l.append(model[initial_field_value_l[i]].as_long())
        return cex_ret_l 
    else:
        return None  # No counterexample found, the candidate function is valid

def cegis_loop():
    # Start with one counterexamples  
    cexamples = [[0 for _ in range(num_pkt_fields + 1)]]
    # Set the iteration bound
    maxIter = 1000
    global synthesis_time, verification_time, total_iterations, search_space_bit
    for i in range(maxIter):
        print("cexamples =", cexamples, "# cex =", len(cexamples))
        start_time = time.time()
        candidate = synthesis_step(cexamples)
        end_time = time.time()
        synthesis_time += end_time - start_time
        if candidate is None:
            print("Synthesis failed, no valid function found.")
            return
        
        # Create a dictionary to store the model's output
        model_dict = {}
        for d in candidate:
            model_dict[d.name()] = candidate[d].as_long()  # Convert Z3 values to Python values

        # Convert the dictionary to JSON
        model_json = json.dumps(model_dict)
        p4_in_json = codegen(model_json, number_of_parser_nodes=num_parser_nodes, size_of_key=size_of_key)
        
        # Go to verificaiton phase
        start_time = time.time()
        cexample = verification_step(model=candidate, cexamples=cexamples)
        end_time = time.time()
        verification_time += end_time - start_time
        if cexample is None:
            print("Final output:", p4_in_json)
            print(f"Valid function found")
            print(f"Synthesis time: {synthesis_time:.2f}s, Verification time: {verification_time:.2f}s, total_iterations = {i+1}, search_space_bit = {search_space_bit}")
            return
        else:
            print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round
            # this is not necessary but I do this for debuging purpose TODO: remove the next line
            cexamples = sorted(cexamples)

# Run the CEGIS loop
cegis_loop()
