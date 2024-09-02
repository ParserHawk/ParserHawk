import random
from bitarray import bitarray

import sys

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

# from bitarray import bitarray

# bit_vector = bitarray('1101101')
# start = 2  # Start from the 3rd bit (0-indexed)
# end = start + 3  # Extract 3 bits

# subrange = bit_vector[start:end]

def node0(Fields, I, pos, idx):
    if idx != 0:
        return Fields, pos, idx
    Fields[0] = I[pos : pos + 4]
    print("Fields[0][3:4] =", Fields[0][3:4])
    if Fields[0][3 : 3 + 1] == bitarray('1'):
        next_idx = 1
    else:
        next_idx = 2
    return Fields, pos + 4, next_idx

def node1(Fields, I, pos, idx):
    if idx != 1:
        return Fields, pos, idx
    Fields[1] = I[pos : pos + 3]
    next_idx = 2
    return Fields, pos + 3, next_idx

def Output_fields_in_int(l):
    ret_str = ""
    for mem in l:
        if isinstance(mem, bitarray):
            ret_str += str(int(mem.to01(), 2)) + ' '
        else:
            ret_str += mem
    print("All these fields' integer values are", ret_str)

def main(argv):
    if len(argv) != 2:
        print("Usage: python3", argv[0], "<input bitstream>")
        sys.exit(1)

    I = bitarray(str(argv[1]))
    random_value0 = random.randint(0, 15)
    field0 = random_value0
    random_value1 = random.randint(0, 7)
    field1 = random_value1

    Fields = [field0, field1]
    pos = 0
    idx = 0
    Fields, pos, idx = node0(Fields, I, pos, idx)
    Fields, pos, idx = node1(Fields, I, pos, idx)
    print("Input bit stream =", I)
    print("Initial Fields =", random_value0, random_value1)
    print("Updated Fields =", Fields)
    Output_fields_in_int(Fields)

if __name__ == "__main__":
    main(sys.argv)