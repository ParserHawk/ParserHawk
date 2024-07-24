#! /usr/bin/python3
import sys
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
