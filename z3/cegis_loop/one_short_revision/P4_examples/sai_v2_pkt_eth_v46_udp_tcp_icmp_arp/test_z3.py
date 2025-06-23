from z3 import *

# Configuration
input_bit_stream_size = 1 + 16 + 8 + 1

pkt_field_size_list = [1, 16, 8, 1, 1, 1, 1, 1]
key_field_list = [0, 16, 8, 0, 0, 0, 0, 0]
num_pkt_fields = len(pkt_field_size_list)
time_to_visit_tcam_tbl = 3

# List the hardware configuration
lookahead_window_size = 0
size_of_key = 16
num_parser_nodes = 8
tcam_num = 6

# Concrete Input Bitstream (as one BitVecVal)
# Let's say we use 60 bits total
input_data = 1048589  # binary string split by fields
Input_bitstream = BitVecVal(input_data, input_bit_stream_size)

# Initial fallback field values (used when conditions fail)
initial_field_val_list = [
    BitVecVal(0, 1),
    BitVecVal(0, 16),
    BitVecVal(0, 8),
    BitVecVal(0, 1),
    BitVecVal(0, 1),
    BitVecVal(0, 1),
    BitVecVal(0, 1),
    BitVecVal(1, 1)
]

# Specification
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
    O_field7 = If(Cond3, Extract(pos_beg, pos_beg  - pkt_field_size_list[7] + 1, Input_bitstream), initial_field_val_list[7])
    
    Cond4 = Extract(7, 0, O_field2) == BitVecVal(0x11, 8)
    Cond5 = Extract(7, 0, O_field2) == BitVecVal(0x06, 8)
    Cond6 = Extract(7, 0, O_field2) == BitVecVal(0x01, 8)
    O_field4 = If(And(Cond1, Cond4), Extract(pos_beg  - pkt_field_size_list[2], pos_beg  - pkt_field_size_list[2] - pkt_field_size_list[4] + 1, Input_bitstream), initial_field_val_list[4])
    O_field5 = If(And(Cond1, Cond5), Extract(pos_beg  - pkt_field_size_list[2], pos_beg  - pkt_field_size_list[2] - pkt_field_size_list[5] + 1, Input_bitstream), initial_field_val_list[5])
    O_field6 = If(And(Cond1, Cond6), Extract(pos_beg  - pkt_field_size_list[2], pos_beg  - pkt_field_size_list[2] - pkt_field_size_list[6] + 1, Input_bitstream), initial_field_val_list[6])

    return [O_field0, O_field1, O_field2, O_field3, O_field4, O_field5, O_field6, O_field7]

# Run and simplify result
outputs = specification(Input_bitstream, initial_field_val_list)
simplified_outputs = [simplify(o) for o in outputs]

# Print results
for i, val in enumerate(simplified_outputs):
    print(f"O_field{i}: {val}")
