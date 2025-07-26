from z3 import *

from bitarray import bitarray
import random
import sys
import json
import random

input_bit_stream_size = 6
# pkt_field_size_list = [16, 25, 8, 1, 1, 1]
pkt_field_size_list = [1, 1, 1, 1, 1]

num_pkt_fields = len(pkt_field_size_list)

# List the hardware configuration
lookahead_window_size = 2
size_of_key = 4

# parser_node_pipe = [1,2,3]
parser_node_pipe = [1,1,1,3]
num_parser_nodes = sum(parser_node_pipe)
# print("num_parser_nodes =", num_parser_nodes)
tcam_num = 3

# mpls[0]: 32-bit field0;
# mpls[1]: 32-bit field1;
# ipv4: 8-bit field2;
# ipv6: 8-bit field3;
# ethernet: 8-bit field4;

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

    condition_parse_mpls_pos_second0 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x4, size_of_key)
    condition_parse_mpls_pos_second1 = Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - 4 + 1, Input_bitstream) == BitVecVal(0x6, size_of_key)
    condition_parse_mpls_pos_second2 = And(Not(condition_parse_mpls_pos_second0), Not(condition_parse_mpls_pos_second1))
    
    O_field2 = If(And(condition_parse_mpls_first1, condition_parse_mpls_pos_first0), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[2] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, condition_parse_mpls_pos_second0), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[2] + 1, Input_bitstream),initial_field_val_list[2]))
    O_field3 = If(And(condition_parse_mpls_first1, condition_parse_mpls_pos_first1), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[3] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, condition_parse_mpls_pos_second1), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[3] + 1, Input_bitstream),initial_field_val_list[3]))
    O_field4 = If(And(condition_parse_mpls_first1, condition_parse_mpls_pos_first2), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[4] + 1, Input_bitstream), 
                  If(And(condition_parse_mpls_first0, condition_parse_mpls_second1, condition_parse_mpls_pos_second2), Extract(input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1], input_bit_stream_size - 1 - pkt_field_size_list[0] - pkt_field_size_list[1] - pkt_field_size_list[4] + 1, Input_bitstream),initial_field_val_list[4]))    
    return [O_field0, O_field1, O_field2, O_field3, O_field4]

cexamples = [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1], [10, 0, 1, 0, 0, 0], [20, 0, 0, 0, 1, 0], [20, 0, 0, 1, 0, 0], [22, 0, 0, 0, 1, 0], [24, 0, 0, 0, 0, 0], [40, 1, 0, 1, 0, 0]]
for example in cexamples:
    x = BitVec('x', input_bit_stream_size)
    s = Solver()
    initial_field_value_l = []
    for i in range(num_pkt_fields):
        initial_field_value_l.append(BitVec(f'initial_field{i}', pkt_field_size_list[i]))
    s.add(x == example[0])
    for i in range(num_pkt_fields):
        s.add(initial_field_value_l[i] == example[i + 1])
    O_Spec = specification(x, initial_field_value_l)
    O_F0 = BitVec('O_F0', 1)
    O_F1 = BitVec('O_F1', 1)
    O_F2 = BitVec('O_F2', 1)
    O_F3 = BitVec('O_F3', 1)
    O_F4 = BitVec('O_F4', 1)
    s.add(O_Spec[0] == O_F0)
    s.add(O_Spec[1] == O_F1)
    s.add(O_Spec[2] == O_F2)
    s.add(O_Spec[3] == O_F3)
    s.add(O_Spec[4] == O_F4)


    if s.check() == sat:
        model = s.model()
        print("example =", example)
        assignments = [(d.name(), model[d]) for d in model]
        sorted_by_name = sorted(assignments, key=lambda x: x[0])
        print("Sorted by name:", sorted_by_name)
        # Return counter example's value, including the input bitstream + all packet fields' initial values
        cex_ret_l = [model[x].as_long()]
        # print("impl output =", model[O_Impl])
        for i in range(num_pkt_fields):
            cex_ret_l.append(model[initial_field_value_l[i]].as_long())
    else:
        print("SAD")