from z3 import *

from generate_z3specification import read_json_and_generate_z3_spec

input_bit_stream_size = 32

x = BitVec('x', input_bit_stream_size)

FILENAME = "tmp/simple_parser.json"
# FILENAME = "partial_key/partial_key.json"
res = read_json_and_generate_z3_spec(x, FILENAME, input_bit_stream_size, [0, 0, 0])

for f in res:
    print(f)
