import json
from z3 import *
import sys
from generate_z3specification import read_json_and_generate_z3_spec

input_bit_stream_size = 656  # for xg_example1, found through hit and trial

x = BitVec('x', input_bit_stream_size)

# FILENAME = "tmp/simple_parser.json"
FILENAME = "xg_example1/xg.json"

if len(sys.argv) > 1: FILENAME = sys.argv[1]

res, inital_vals = read_json_and_generate_z3_spec(x, input_bit_stream_size, FILENAME)

print("# Header and Header Sizes:")
info = {}
for v in inital_vals:
    name = v.removeprefix("initial_val_")
    size = inital_vals[v][1]
    info[name] = size
print(json.dumps(info, indent=4))
print()

print("# All Required Initial Values (and their respective sizes):")
for v in inital_vals:
    name = inital_vals[v][0]
    size = inital_vals[v][1]
    print(name, " = ", "BitVec("+ f"'{name}', {size}" +")")
print()
print("# All Z3 Expressions:")
for f in res:
    for k in f:
        print(k, " = ", f[k])