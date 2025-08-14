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
header mpls_t {
    bit<1>  bos;
    bit<20> label;
    bit<3>  exp;
    bit<8>  ttl;
}

header ipv4_t {
    bit<8>  f8;
}

header ipv6_t {
    bit<8>  f8;
}

header ethernet_t {
    bit<8>  f8;
}

struct headers {
    ipv4_t ipv4;
    ipv6_t ipv6;
    ethernet_t eth;
    mpls_t[3]                               mpls;
}

state start {
    transition parse_mpls;
}
state parse_mpls {
    b.extract(hdr.mpls.next);
    transition select(hdr.mpls.last.bos) {
        1w0: parse_mpls;
        1w1: parse_mpls_bos;
        default: accept;
    }
}
state parse_mpls_bos {
    transition select((b.lookahead<bit<4>>())[3:0]) {
        4w0x4: parse_mpls_inner_ipv4;
        4w0x6: parse_mpls_inner_ipv6;
        default: parse_eompls;
    }
}
state parse_mpls_inner_ipv4 {
    b.extract(hdr.ipv4);
    transition accept;
}
state parse_mpls_inner_ipv6 {
    b.extract(hdr.ipv6);
    transition accept;
}
state parse_eompls {
    b.extract(hdr.eth);
    transition accept;
}
"""
synthesis_time = 0
verification_time = 0
total_iterations = 0
has_run = False  # global guard
search_space_bit = 0

input_bit_stream_size = 6
# pkt_field_size_list = [16, 25, 8, 1, 1, 1]
pkt_field_size_list = [1, 1, 1, 1, 1]

num_pkt_fields = len(pkt_field_size_list)

# List the hardware configuration
lookahead_window_size = 4
size_of_key = 4

num_parser_nodes = 6
# print("num_parser_nodes =", num_parser_nodes)
tcam_num = 4

# TODO: should generate the specification automatically
# Input: Input_bitstream with the type bitVec var in z3, and initial value of all fields
# Output: Updated value of all packet fields
def specification(Input_bitstream, initial_field_val_list):
    # out_field1 = BitVec(f'out_field0_{I_val}', 4)
    #      1   1  1  1 0 0 0 0 1 1 1 0 0 0
    #  pos 0   1  2  3 4
    #  idx 13 12 11 10 9 8 
    O_field0 = Extract(input_bit_stream_size - 1, input_bit_stream_size - 1 - pkt_field_size_list[0] + 1, Input_bitstream) #node 0
    condition_parse_mpls_first0 = Extract(0, 0, O_field0) == BitVecVal(0x0, 1)
    condition_parse_mpls_first1 = Extract(0, 0, O_field0) == BitVecVal(0x1, 1)
    O_field1 = If(condition_parse_mpls_first0, Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] + 1, Input_bitstream), initial_field_val_list[1])
    condition_parse_mpls_second0 = Extract(0, 0, O_field1) == BitVecVal(0x0, 1)
    condition_parse_mpls_second1 = Extract(0, 0, O_field1) == BitVecVal(0x1, 1)
    
    condition_parse_mpls_pos_first0 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x4, size_of_key)
    condition_parse_mpls_pos_first1 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x6, size_of_key)
    condition_parse_mpls_pos_first2 = And(Not(condition_parse_mpls_pos_first0), Not(condition_parse_mpls_pos_first1))
    Or_conditions1 = Or(Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x1, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x2, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x3, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x5, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x7, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0x9, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xa, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xb, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xc, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xd, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xe, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - 4 + 1, Input_bitstream) == BitVecVal(0xf, size_of_key),
                       condition_parse_mpls_pos_first2)

    condition_parse_mpls_pos_second0 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x4, size_of_key)
    condition_parse_mpls_pos_second1 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x6, size_of_key)
    
    condition_parse_mpls_pos_second2 = And(Not(condition_parse_mpls_pos_second0), Not(condition_parse_mpls_pos_second1))
    Or_conditions2 = Or(Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x1, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x2, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x3, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x5, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x7, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x9, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xa, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xb, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xc, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xd, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xe, size_of_key),
                       Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0xf, size_of_key),
                       condition_parse_mpls_pos_second2)
    
    
    O_field2 = If(And(condition_parse_mpls_first1, condition_parse_mpls_pos_first0), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[2] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, condition_parse_mpls_pos_second0), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[2] + 1, Input_bitstream),initial_field_val_list[2]))
    O_field3 = If(And(condition_parse_mpls_first1, condition_parse_mpls_pos_first1), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[3] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, condition_parse_mpls_pos_second1), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[3] + 1, Input_bitstream),initial_field_val_list[3]))
    O_field4 = If(And(condition_parse_mpls_first1, Or_conditions1), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[4] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, Or_conditions2), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[4] + 1, Input_bitstream),initial_field_val_list[4]))    
    return [O_field0, O_field1, O_field2, O_field3, O_field4]

# TODO: should generate the spec automatically
# Input: Input_bitstream with the type string, and initial value of all fields
# Output: updated fields' value in int type
def spec(Input_bitstream, initial_list):
    # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
    Fields = ["" for _ in range(num_pkt_fields)]
    Fields[0] = Input_bitstream[0 : pkt_field_size_list[0]]
    if Fields[0][0] == "0":
        Fields[1] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[1]]
        if Fields[1][0] == "1":
            if Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0100":
                Fields[2] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[2]]
            elif Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0110":
                Fields[3] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[3]]
            elif Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0001" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0010" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0011" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0101" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0111" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1000" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1001" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1010" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1011" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1100" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1101" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1110" or Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "1111":
                Fields[4] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[4]]
            else:
                Fields[4] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[4]]    
    else:
        if Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0100":
            Fields[2] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[2]]
        elif Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0110":
            Fields[3] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[3]]
        elif Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0001" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0010" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0011" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0101" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0111" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1000" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1001" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1010" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1011" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1100" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1101" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1110" or Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "1111":
            Fields[4] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[4]]
        else:
            Fields[4] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[4]]
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
        ret_idx = If(And(assignments[i] == node_id, (Extract(size_of_key - 1, 0, key_sel) & key_mask_total_list[i]) == key_val_total_list[i]), tran_idx_total_list[i], ret_idx)

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
    field_l = []
    input_field0 = BitVec(f'input_field0_{testcaseID}', pkt_field_size_list[0])
    field_l.append(input_field0)
    input_field1 = BitVec(f'input_field1_{testcaseID}', pkt_field_size_list[1])
    field_l.append(input_field1)
    input_field2 = BitVec(f'input_field2_{testcaseID}', pkt_field_size_list[2])
    field_l.append(input_field2)
    input_field3 = BitVec(f'input_field3_{testcaseID}', pkt_field_size_list[3])
    field_l.append(input_field3)
    input_field4 = BitVec(f'input_field4_{testcaseID}', pkt_field_size_list[4])
    field_l.append(input_field4)
    
    # Define constraints for this temporary BitVec based on the counterexample
    constraint = []
    constraint.append(Input_bitstream == I_val)  # Constraint depends on the counterexample
    constraint.append(input_field0 == random_initial_value_list[0])
    constraint.append(input_field1 == random_initial_value_list[1])
    constraint.append(input_field2 == random_initial_value_list[2])
    constraint.append(input_field3 == random_initial_value_list[3])
    constraint.append(input_field4 == random_initial_value_list[4])
    # return Input_bitstream, [input_field0, input_field1, input_field2], extract_status, constraint
    return Input_bitstream, field_l, constraint

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
    for k in range(3):
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

# Generate default transition index in each parser node
# e.g., default_idx_node0 = Int('default_idx_node0')
def default_idx_gen(num_parser_nodes):
    default_idx_node_list = []
    for nodeID in range(num_parser_nodes):
        default_idx_node_list.append(Int(f'default_idx_node{nodeID}'))
    return default_idx_node_list

def synthesis_step(cexamples):
    # print("Enter synthsis phase")
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

    s.add(Flags[0][0] == 1)
    s.add(Flags[1][1] == 1)
    s.add(Flags[2][2] == 1)
    s.add(Flags[3][3] == 1)
    s.add(Flags[4][4] == 1)

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
    assignments = [Int(f'assign_{i}') for i in range(tcam_num)]
    key_val_total_list = [BitVec(f'key_val{i}', size_of_key) for i in range(tcam_num)]
    key_mask_total_list = [BitVec(f'key_mask{i}', size_of_key) for i in range(tcam_num)]
    tran_idx_total_list = [Int(f'tran_idx{i}') for i in range(tcam_num)]
    constraints = [assignments[i] >= 0 for i in range(tcam_num)]
    for i in range(tcam_num - 1):
        constraints.append(assignments[i] <= assignments[i + 1])
    for i in range(len(alloc_matrix)):
        for j in range(len(alloc_matrix[i]) - 1):
            s.add(alloc_matrix[i][j] == alloc_matrix[i][j + 1])
    for i in range(tcam_num):
        s.add(key_mask_total_list[i] == 0xF)
        s.add(Or(key_val_total_list[i] == 1, key_val_total_list[i] == 4, key_val_total_list[i] == 6))
    s.add(constraints)
    global has_run, search_space_bit
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
    
    assignments = [Int(f'assign_{i}') for i in range(tcam_num)]
    key_val_total_list = [BitVec(f'key_val{i}', size_of_key) for i in range(tcam_num)]
    key_mask_total_list = [BitVec(f'key_mask{i}', size_of_key) for i in range(tcam_num)]
    tran_idx_total_list = [Int(f'tran_idx{i}') for i in range(tcam_num)]

    for i in range(len(assignments)):
        value = model.evaluate(assignments[i], model_completion=True)
        if value is not None:
            s.add(assignments[i] == value.as_long())
        else:
            s.add(assignments[i] == tcam_num)
    for i in range(len(key_val_total_list)):
        value = model.evaluate(key_val_total_list[i], model_completion=True)
        if value is not None:
            s.add(key_val_total_list[i] == value.as_long())
        else:
            s.add(key_val_total_list[i] == -1)
    for i in range(len(key_mask_total_list)):
        value = model.evaluate(key_mask_total_list[i], model_completion=True)
        if value is not None:
            s.add(key_mask_total_list[i] == value.as_long())
        else:
            s.add(key_mask_total_list[i] == -1)
    for i in range(len(tran_idx_total_list)):
        value = model.evaluate(tran_idx_total_list[i], model_completion=True)
        if value is not None:
            s.add(tran_idx_total_list[i] == value.as_long())
        else:
            s.add(tran_idx_total_list[i] == num_parser_nodes)

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