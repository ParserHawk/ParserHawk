from z3 import *

from bitarray import bitarray
import random
import sys
import json
import random
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))
# Now you can import the library from Folder B
from practical_ex.code_gen_big_tcam import *

"""
spec:
state parse_packet_out_header {
    packet.extract(headers.packet_out_header);  // 1-bit
    transition parse_ethernet;
  }

  state parse_ethernet {
    packet.extract(headers.ethernet);   // 16-bit
    transition select(headers.ethernet.ether_type) {
      0x0001: accept;
      0x0002: accept;
      0x0003: accept;
      0x0004: accept;
      0x0005: accept;
      0x0006: accept;
      0x0007: accept;
      0x0008: accept;
      0x0009: accept;
      0x000A: accept;
      0x000B: accept;
      0x000C: accept;
      0x000D: accept;
      0x000E: accept;
      0x000F: accept;
      0x0010: accept;
      0x0011: accept;
      0x0012: accept;
      0x0013: accept;
      0x0014: accept;
      0x0015: accept;
      0x0016: accept;
      0x0017: accept;
      0x0018: accept;
      0x0019: accept;
      0x001A: accept;
      0x001B: accept;
      0x001C: accept;
      0x001D: accept;
      0x001E: accept;
      0x001F: accept;
      0x0020: accept;
      0x0021: accept;
      0x0022: accept;
      0x0023: accept;
      0x0024: accept;
      0x0025: accept;
      0x0026: accept;
      0x0027: accept;
      0x0028: accept;
      0x0029: accept;
      0x002A: accept;
      0x002B: accept;
      0x002C: accept;
      0x002D: accept;
      0x002E: accept;
      0x002F: accept;
      0x0030: accept;
      0x0031: accept;
      0x0032: accept;
      0x0033: accept;
      0x0034: accept;
      0x0035: accept;
      0x0036: accept;
      0x0037: accept;
      0x0038: accept;
      0x0039: accept;
      0x003A: accept;
      0x003B: accept;
      0x003C: accept;
      0x003D: accept;
      0x003E: accept;
      0x003F: accept;
      0x0040: accept;
      0x0041: accept;
      0x0042: accept;
      0x0043: accept;
      0x0044: accept;
      0x0045: accept;
      0x0046: accept;
      0x0047: accept;
      0x0048: accept;
      0x0049: accept;
      0x004A: accept;
      0x004B: accept;
      0x004C: accept;
      0x004D: accept;
      0x004E: accept;
      0x004F: accept;
      0x0050: accept;
      0x0051: accept;
      0x0052: accept;
      0x0053: accept;
      0x0054: accept;
      0x0055: accept;
      0x0056: accept;
      0x0057: accept;
      0x0058: accept;
      0x0059: accept;
      0x005A: accept;
      0x005B: accept;
      0x005C: accept;
      0x005D: accept;
      0x005E: accept;
      0x005F: accept;
      0x0060: accept;
      0x0061: accept;
      0x0062: accept;
      0x0063: accept;
      0x0064: accept;
      0x0065: accept;
      0x0066: accept;
      0x0067: accept;
      0x0068: accept;
      0x0069: accept;
      0x006A: accept;
      0x006B: accept;
      0x006C: accept;
      0x006D: accept;
      0x006E: accept;
      0x006F: accept;
      0x0070: accept;
      0x0071: accept;
      0x0072: accept;
      0x0073: accept;
      0x0074: accept;
      0x0075: accept;
      0x0076: accept;
      0x0077: accept;
      0x0078: accept;
      0x0079: accept;
      0x007A: accept;
      0x007B: accept;
      0x007C: accept;
      0x007D: accept;
      0x007E: accept;
      0x007F: accept;
      0x0080: accept;
      0x0081: accept;
      0x0082: accept;
      0x0083: accept;
      0x0084: accept;
      0x0085: accept;
      0x0086: accept;
      0x0087: accept;
      0x0088: accept;
      0x0089: accept;
      0x008A: accept;
      0x008B: accept;
      0x008C: accept;
      0x008D: accept;
      0x008E: accept;
      0x008F: accept;
      0x0090: accept;
      0x0091: accept;
      0x0092: accept;
      0x0093: accept;
      0x0094: accept;
      0x0095: accept;
      0x0096: accept;
      0x0097: accept;
      0x0098: accept;
      0x0099: accept;
      0x009A: accept;
      0x009B: accept;
      0x009C: accept;
      0x009D: accept;
      0x009E: accept;
      0x009F: accept;
      0x00A0: accept;
      0x00A1: accept;
      0x00A2: accept;
      0x00A3: accept;
      0x00A4: accept;
      0x00A5: accept;
      0x00A6: accept;
      0x00A7: accept;
      0x00A8: accept;
      0x00A9: accept;
      0x00AA: accept;
      0x00AB: accept;
      0x00AC: accept;
      0x00AD: accept;
      0x00AE: accept;
      0x00AF: accept;
      0x00B0: accept;
      0x00B1: accept;
      0x00B2: accept;
      0x00B3: accept;
      0x00B4: accept;
      0x00B5: accept;
      0x00B6: accept;
      0x00B7: accept;
      0x00B8: accept;
      0x00B9: accept;
      0x00BA: accept;
      0x00BB: accept;
      0x00BC: accept;
      0x00BD: accept;
      0x00BE: accept;
      0x00BF: accept;
      0x00C0: accept;
      0x00C1: accept;
      0x00C2: accept;
      0x00C3: accept;
      0x00C4: accept;
      0x00C5: accept;
      0x00C6: accept;
      0x00C7: accept;
      0x00C8: accept;
      0x00C9: accept;
      0x00CA: accept;
      0x00CB: accept;
      0x00CC: accept;
      0x00CD: accept;
      0x00CE: accept;
      0x00CF: accept;
      0x00D0: accept;
      0x00D1: accept;
      0x00D2: accept;
      0x00D3: accept;
      0x00D4: accept;
      0x00D5: accept;
      0x00D6: accept;
      0x00D7: accept;
      0x00D8: accept;
      0x00D9: accept;
      0x00DA: accept;
      0x00DB: accept;
      0x00DC: accept;
      0x00DD: accept;
      0x00DE: accept;
      0x00DF: accept;
      0x00E0: accept;
      0x00E1: accept;
      0x00E2: accept;
      0x00E3: accept;
      0x00E4: accept;
      0x00E5: accept;
      0x00E6: accept;
      0x00E7: accept;
      0x00E8: accept;
      0x00E9: accept;
      0x00EA: accept;
      0x00EB: accept;
      0x00EC: accept;
      0x00ED: accept;
      0x00EE: accept;
      0x00EF: accept;
      0x00F0: accept;
      0x00F1: accept;
      0x00F2: accept;
      0x00F3: accept;
      0x00F4: accept;
      0x00F5: accept;
      0x00F6: accept;
      0x00F7: accept;
      0x00F8: accept;
      0x00F9: accept;
      0x00FA: accept;
      0x00FB: accept;
      0x00FC: accept;
      0x00FD: accept;
      0x00FE: accept;
      0x00FF: accept;
      ETHERTYPE_IPV6: parse_ipv6; // 0x86dd
      ETHERTYPE_ARP:  parse_arp;  // 0x0806
      _:              accept;
    }
  }

  state parse_ipv4 {  
    packet.extract(headers.ipv4); // 1-bit
    transition accept;
  }

  state parse_ipv6 {
    packet.extract(headers.ipv6);  // 1-bit
    transition accept;
  }

  state parse_arp {
    packet.extract(headers.arp);  // 1-bit
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
time_to_visit_tcam_tbl = 2

# List the hardware configuration
lookahead_window_size = 2
size_of_key = 16
num_parser_nodes = 5
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
    for i in range(len(pkt_field_size_list)):
        ret_l.append(dynamic_extract_loop(s, pos, I, Dist, F[i], pkt_field_size_list[i], field_id=i))
    return ret_l

def generate_update_field_val(idx, Dist, F, key_expr_list, alloc_matrix, s, node_id):
    ret_l = []
    for i in range(len(pkt_field_size_list)):
        # s.add(Implies(Dist[i] == 1, key_expr_list[i] != None))
        ret_l.append(If(And(idx == node_id, Dist[i] == 1), key_expr_list[i], F[i]))
    return ret_l

def generate_tran_key(alloc_matrix, node_id, update_field_val_l, 
                      post_node_pos, Lookahead, I, s):
    dummy = BitVec('dummy', 1)
    s.add(dummy == 0)
    key_sel = None
    # Only extracted fields can be used as the state transition key

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
        total = sum(pkt_field_size_list) + lookahead_window_size
    for i in range(total, size_of_key):
        key_sel = Concat(dummy, key_sel)
    return key_sel

def post_node_pos(idx, Dist, node_id, alloc_matrix, pos):
    # Start with the base case: if none of Dist[i] == 1 apply, return pos
    result = pos
    
    # Loop over the indices and build the nested If conditions
    for i in range(len(Dist) - 1, -1, -1):  # Reverse order to build nested If from the inside out
        result = If(Dist[i] == 1, pos + pkt_field_size_list[i], result)
    
    # Add the outermost condition for idx
    return If(idx == node_id, result, pos)

# def generate_return_idx(key_val_list, key_mask_list, tran_idx_list, default_idx_node1, num_transitions, size_of_key, key_sel, idx, node_id):
def generate_return_idx(assignments, key_val_total_list, key_mask_total_list, tran_idx_total_list, default_idx_node1, size_of_key, key_sel, idx, node_id):
    ret_idx = default_idx_node1  # Default case
    # Reverse the order because we want to make the TCAM entry with smaller number to dominate the transition logic
    for i in range(tcam_num - 1, -1, -1):
        # key_val_list = BitVec(name, size_of_key);
        ret_idx = If(And(assignments[i] == node_id, (Extract(size_of_key - 1, 0, key_sel) & key_mask_total_list[i]) == key_val_total_list[i] & key_mask_total_list[i]), tran_idx_total_list[i], ret_idx)

    # Final state transition for idx == 1
    ret_idx = If(idx == node_id, ret_idx, idx)
    return ret_idx

def update_extract_states(idx, Dist, node_id, num_pkt_fields):
    ret_l = []
    # Update the extraction status only if this node does this packet field extraction
    for i in range(num_pkt_fields):
        ret_l.append(If(And(idx == node_id, Dist[i] == 1), 1))
    return ret_l


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
    
    Out_Fields = Input_Fields
    post_pos = pos
    # always visit node 0 in the beginning
    Out_Fields, post_pos, idx = new_node(0, Flags[0], Out_Fields, Input_bitstream, 
                                                                        idx=idx, pos=post_pos, alloc_matrix=alloc_matrix, 
                                                                        Lookahead=Lookahead, 
                                                                        # key_val_list=key_val_2D_list[0], 
                                                                        # key_mask_list=key_mask_2D_list[0], 
                                                                        # tran_idx_list=tran_idx_2D_list[0],
                                                                        assignments=assignments,
                                                                        key_val_total_list=key_val_total_list, 
                                                                        key_mask_total_list=key_mask_total_list, 
                                                                        tran_idx_total_list=tran_idx_total_list,
                                                                        default_idx_node=default_idx_node_list[0], 
                                                                        s=s)
    for k in range(time_to_visit_tcam_tbl):
        results = []
        for i in range(num_parser_nodes):
            condition = idx == i
            out_fields, post_pos_i, idx_i = new_node(
                i, Flags[i], Out_Fields, Input_bitstream, 
                idx=idx, pos=post_pos, alloc_matrix=alloc_matrix, 
                Lookahead=Lookahead, 
                # key_val_list=key_val_2D_list[0], 
                # key_mask_list=key_mask_2D_list[0], 
                # tran_idx_list=tran_idx_2D_list[0],
                assignments=assignments,
                key_val_total_list=key_val_total_list, 
                key_mask_total_list=key_mask_total_list, 
                tran_idx_total_list=tran_idx_total_list,
                default_idx_node=default_idx_node_list[i], 
                s=s
            )
            results.append((condition, out_fields, post_pos_i, idx_i))

        # Process the results to update Out_Fields, post_pos, idx, and post_extract_status
        for condition, out_fields_i, post_pos_i, idx_i in results:
            Out_Fields = [If(condition, then_ele, else_ele) for then_ele, else_ele in zip(out_fields_i, Out_Fields)]
            post_pos = If(condition, post_pos_i, post_pos)
            idx = If(condition, idx_i, idx)

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
def alloc_matrix_gen(key_field_list):
    alloc_matrix = []
    # Loop to define the variables and populate the matrix
    for i in range(len(key_field_list)):  
        row = []  
        for j in range(key_field_list[i]):
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

# Generate default transition index in each parser node
# e.g., default_idx_node0 = Int('default_idx_node0')
def default_idx_gen(num_parser_nodes):
    default_idx_node_list = []
    for nodeID in range(num_parser_nodes):
        default_idx_node_list.append(Int(f'default_idx_node{nodeID}'))
    return default_idx_node_list

def synthesis_step(cexamples):
    # print("Enter synthsis phase")
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

    alloc_matrix = alloc_matrix_gen(key_field_list=key_field_list)
    
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)
        
    # key_val_2D_list, key_mask_2D_list = key_val_gen(num_transitions=num_transitions, size_of_key=size_of_key, 
    #                               num_parser_nodes=num_parser_nodes)
    # tran_idx_2D_list = tran_idx_gen(num_transitions=num_transitions,num_parser_nodes=num_parser_nodes)
    
    default_idx_node_list = default_idx_gen(num_parser_nodes=num_parser_nodes)

    # NEW CODE
    assignments = [Int(f'assign_{i}') for i in range(tcam_num)]
    key_val_total_list = [BitVec(f'key_val{i}', size_of_key) for i in range(tcam_num)]
    
    key_mask_total_list = [BitVec(f'key_mask{i}', size_of_key) for i in range(tcam_num)]
    
    tran_idx_total_list = [Int(f'tran_idx{i}') for i in range(tcam_num)]
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i]) - 1):
            s.add(alloc_matrix[i][j] == alloc_matrix[i][j + 1])
    for i in range(tcam_num):
        # s.add(key_mask_total_list[i] == 0xFFFF)
        s.add(Or(key_val_total_list[i] == 0x0800, key_val_total_list[i] == 0x86dd, 
                 key_val_total_list[i] == 0x0806, And(key_val_total_list[i] >= 0x0, key_val_total_list[i] <= 0xFF)))
    # Update search space
    if not has_run:
        for i in range(len(Flags)): # Flags
            search_space_bit += len(Flags[i])
        for i in range(len(alloc_matrix)): # alloc_matric
            search_space_bit += len(alloc_matrix[i]) * math.ceil(math.log2(num_parser_nodes + 1))
        for i in range(len(Lookahead)): # Lookahead
            search_space_bit += len(Lookahead[i]) * math.ceil(math.log2(num_parser_nodes + 1))
        search_space_bit += num_parser_nodes * math.ceil(math.log2(num_parser_nodes + 1)) # default transition
        search_space_bit += tcam_num * math.ceil(math.log2(num_parser_nodes + 1)) # Assignment
        search_space_bit += tcam_num * size_of_key # Value
        search_space_bit += tcam_num * size_of_key # Mask
        search_space_bit += tcam_num * math.ceil(math.log2(num_parser_nodes + 1)) # Transition
        has_run = True

    constraints = [And(assignments[i] >= 0, assignments[i] <= num_parser_nodes) for i in range(tcam_num)]
    for i in range(tcam_num - 1):
        constraints.append(assignments[i] <= assignments[i + 1])
    s.add(constraints)
    s.add(Flags[0][0] == 1)
    s.add(Flags[1][1] == 1)
    s.add(Flags[2][2] == 1)
    s.add(Flags[3][3] == 1)
    s.add(Flags[4][4] == 1)
    
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
    # print("Enter verification phase")
    # Try to find a counterexample where f(x) != g(x)
    x = BitVec('x', input_bit_stream_size)
    s = Solver()

    Flags = flag_gen(num_parser_nodes=num_parser_nodes, num_pkt_fields=num_pkt_fields)    
    alloc_matrix = alloc_matrix_gen(key_field_list=key_field_list)
    Lookahead = lookahead_gen(num_parser_nodes=num_parser_nodes, lookahead_window_size=lookahead_window_size)
    # Force z3's variables to be the value output from the synthesis phase
    for i in range(len(Flags)):
        for j in range(len(Flags[i])):
            if Flags[i][j].decl() in [d for d in model.decls()]:
                value = model.evaluate(Flags[i][j], model_completion=False).as_long()
            else:
                value = 0  # your chosen default
            s.add(Flags[i][j] == value)
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i])):
            if alloc_matrix[i][j].decl() in [d for d in model.decls()]:
                value = model.evaluate(alloc_matrix[i][j], model_completion=False).as_long()
            else:
                value = -1  # your chosen default
            s.add(alloc_matrix[i][j] == value)
    for i in range(len(Lookahead)):
        for j in range(len(Lookahead[i])):
            if Lookahead[i][j].decl() in [d for d in model.decls()]:
                value = model.evaluate(Lookahead[i][j], model_completion=False).as_long()
            else:
                value = 0  # your chosen default
            s.add(Lookahead[i][j] == value)
    
    assignments = [Int(f'assign_{i}') for i in range(tcam_num)]
    key_val_total_list = [BitVec(f'key_val{i}', size_of_key) for i in range(tcam_num)]
    key_mask_total_list = [BitVec(f'key_mask{i}', size_of_key) for i in range(tcam_num)]
    tran_idx_total_list = [Int(f'tran_idx{i}') for i in range(tcam_num)]

    for i in range(len(assignments)):
        if assignments[i].decl() in [d for d in model.decls()]:
            value = model.evaluate(assignments[i], model_completion=False).as_long()
        else:
            value = tcam_num  # your chosen default
        s.add(assignments[i] == value)

    for i in range(len(key_val_total_list)):
        if key_val_total_list[i].decl() in [d for d in model.decls()]:
            value = model.evaluate(key_val_total_list[i], model_completion=False).as_long()
        else:
            value = -1  # your chosen default
        s.add(key_val_total_list[i] == value)
        
    for i in range(len(key_mask_total_list)):
        if key_mask_total_list[i].decl() in [d for d in model.decls()]:
            value = model.evaluate(key_mask_total_list[i], model_completion=False).as_long()
        else:
            value = 0  # your chosen default
        s.add(key_mask_total_list[i] == value)
        
    for i in range(len(tran_idx_total_list)):
        if tran_idx_total_list[i].decl() in [d for d in model.decls()]:
            value = model.evaluate(tran_idx_total_list[i], model_completion=False).as_long()
        else:
            value = num_parser_nodes  # your chosen default
        s.add(tran_idx_total_list[i] == value)

    default_idx_node_list = default_idx_gen(num_parser_nodes=num_parser_nodes)
    for i in range(len(default_idx_node_list)):
        if default_idx_node_list[i].decl() in [d for d in model.decls()]:
            value = model.evaluate(default_idx_node_list[i], model_completion=False).as_long()
        else:
            value = num_parser_nodes + 1 # your chosen default
        s.add(default_idx_node_list[i] == value)

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
        # print("cexamples =", cexamples, "# cex =", len(cexamples))
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
            # print("Final output:", p4_in_json)
            print(f"Valid function found")
            print(f"Synthesis time: {synthesis_time:.2f}s, Verification time: {verification_time:.2f}s, total_iterations = {i+1}, search_space_bit = {search_space_bit}")
            print(f"num of TCAM entry: {tcam_num}")
            return
        else:
            # print(f"Counterexample found: x = {cexample}")
            cexamples.append(cexample)  # Add the counterexample for the next round
            # this is not necessary but I do this for debuging purpose TODO: remove the next line
            cexamples = sorted(cexamples)

# Run the CEGIS loop
cegis_loop()