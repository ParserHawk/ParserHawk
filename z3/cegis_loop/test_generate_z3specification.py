from z3 import *

from generate_z3specification import read_json_and_generate_z3_spec

input_bit_stream_size = 656  # for xg_example1, found through hit and trial

x = BitVec('x', input_bit_stream_size)

# FILENAME = "tmp/simple_parser.json"
FILENAME = "xg_example1/xg.json"

res = read_json_and_generate_z3_spec(x, FILENAME, input_bit_stream_size, [0]*100)

for f in res:
    print(f)