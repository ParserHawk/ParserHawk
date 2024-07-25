#! /usr/bin/python3
import sys
import z3

# to assign unique names to each z3 var
z3_var_counter = 0

# z3 solver
solver = z3.Solver()

lines = sys.stdin.readlines()
io_pairs = []
for line in lines:
    line = line.replace(' ', '')
    input_bitstream, output_headers = line.strip('\n').split('->')
    output_headers = output_headers.split(',')
    if input_bitstream != ''.join(output_headers):
        print("Bad input: output headers must concatenate to form input string")
        sys.exit(1)
    io_pairs.append((input_bitstream, output_headers))
print(io_pairs)

# Z3 stuff below ...
input_bitstreams_z3 = []
z3_var_counter += 1
offset_z3 = z3.Int(z3_var_counter)
for io_pair in io_pairs:
    z3_var_counter += 1
    input_bitstreams_z3.append(z3.String(z3_var_counter))
    input_str = io_pair[0]
    print(input_str)
    output_header_vector = io_pair[1]
    print(output_header_vector)
    assert(len(output_header_vector) == 2) # for now, just handle inputs of length 2
    current_input_z3 = input_bitstreams_z3[-1]
    solver.add(current_input_z3 == input_str)
    solver.add(z3.SubString(current_input_z3, 0, offset_z3) == output_header_vector[0])
    solver.add(z3.SubString(current_input_z3, offset_z3, z3.Length(current_input_z3)) == output_header_vector[1])

print(solver.check())
print(solver.model())
