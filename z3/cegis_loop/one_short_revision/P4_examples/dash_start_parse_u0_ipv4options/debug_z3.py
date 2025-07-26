from z3 import *

# Packet field sizes
input_bit_stream_size = 16+4+1

pkt_field_size_list = [16, 4, 1]
key_field_list = [16, 4, 0]
num_pkt_fields = len(pkt_field_size_list)


# Declare bitstream and initial values
Input_bitstream = BitVec('Input_bitstream', input_bit_stream_size)
initial_field_val_list = [
    BitVecVal(0, pkt_field_size_list[0]),  # Unused in this spec
    BitVecVal(0xf, pkt_field_size_list[1]),  # fallback for field1
    BitVecVal(0x7, pkt_field_size_list[2])   # fallback for field2
]

def specification(Input_bitstream, initial_field_val_list):
    # Field 0
    O_field0 = Extract(input_bit_stream_size - 1,
                       input_bit_stream_size - pkt_field_size_list[0],
                       Input_bitstream)
    post_field0_pos = input_bit_stream_size - pkt_field_size_list[0]

    # Condition and field 1
    Cond_field1 = Extract(15, 0, O_field0) == BitVecVal(0x876d, 16)
    O_field1 = If(Cond_field1,
                  Extract(post_field0_pos - 1,
                          post_field0_pos - pkt_field_size_list[1],
                          Input_bitstream),
                  initial_field_val_list[1])

    # Condition and field 2
    field1_val = Extract(pkt_field_size_list[1] - 1, 0, O_field1)
    Cond_field1_to_2 = Or(field1_val == BitVecVal(1, 4),
                          field1_val == BitVecVal(2, 4),
                          field1_val == BitVecVal(3, 4))
    Cond_field2 = And(Cond_field1, Cond_field1_to_2)
    post_field1_pos = post_field0_pos - pkt_field_size_list[1]

    O_field2 = If(Cond_field2,
                  Extract(post_field1_pos - 1,
                          post_field1_pos - pkt_field_size_list[2],
                          Input_bitstream),
                  initial_field_val_list[2])

    return [O_field0, O_field1, O_field2]

# ==== Simulation ====

# (1) Provide a concrete input: e.g., 0b11110000111000
concrete_bits = 0b100001110110110100000
Input_concrete = BitVecVal(concrete_bits, input_bit_stream_size)

# (2) Simulate
fields = specification(Input_concrete, initial_field_val_list)

# (3) Print results
print("Output Fields:")
for i, field in enumerate(fields):
    print(f"O_field{i} =", simplify(field))
