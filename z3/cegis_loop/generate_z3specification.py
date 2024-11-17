import json
from typing import List
from z3 import BitVec, Extract, If, And, BitVecVal

'''
Makes it easy to access data by name
'''
def make_named_dict(data):
    res = {}
    for d in data:
        res[d["name"]] = d
    return res

def get_per_field_binary_value(binary_value: str, fields_used_in_transition_key: List[str], field_size_by_name):
    res = []
    for f in reversed(fields_used_in_transition_key):
        size = field_size_by_name[f]
        tmp = "0"
        if (size < len(binary_value)):
            tmp = binary_value[-size:]
            binary_value = binary_value[:-size]
        res = [(f, tmp)] + res
    return res
'''
DFS: Extracts field from a state and transitions to the next state
'''
def dfs(curr, offset, headers, header_types, states, input, z3_result, len_, cond, header_default_vals):
    st = states[curr]

    for o in st["parser_ops"]:
        if o["op"] == "extract":
            op = o
            break

    assert len(op["parameters"]) == 1, "Exactly one param supported yet!"
    param = op["parameters"][0]

    assert param["type"] == "regular", "Regular fields supported yet"

    hdr_name = param["value"]
    hdr_type_info = header_types[headers[hdr_name]["header_type"]]
    fields = hdr_type_info["fields"]

    size_of_hdr = 0
    field_size_by_name = {}
    field_pos_by_name = {}

    _start = 0
    for field in fields:
        size_of_hdr += field[1]
        field_size_by_name[field[0]] = field[1]

        field_pos_by_name[field[0]] = (_start, _start+field[1])
        _start += field[1]

    hi = (len_ - offset) - 1
    lo = (len_ - (offset + size_of_hdr - 1)) - 1
    assert hi >= lo, "Wrong hi, lo in z3_hdr extraction"
    assert lo >= 0, "lo too low in z3_hdr extraction"
    
    assert hdr_name in header_default_vals, f"Initial value not found for {hdr_name}"
    z3_hdr = If(cond, Extract(hi, lo, input), header_default_vals[hdr_name][0])  # constructing z3 expression

    offset += size_of_hdr
    z3_result += [{hdr_name: z3_hdr}]

    # Assuming that all the fields used in transition belong to the header that was extracted in the current state
    fields_used_in_transition_key = []
    for tk in st["transition_key"]:
        assert tk["value"][0] == hdr_name, "A field of non-current header was used in transition, a no no!!"
        assert tk["type"] == "field", "Only fields supported in transition key"

        fields_used_in_transition_key += [tk["value"][1]]

    for t in st["transitions"]:
        assert t["mask"] == None, "Not accounting for mask right now"
        assert t["type"] in ["hexstr", "default"], f"Only hex type supported yet, found {t['type']}"

        if t["type"] == "default":
            next_st = t["next_state"]
            if next_st == None: continue
            new_cond = True
            dfs(next_st, offset, headers, header_types, states, input, z3_result, len_, new_cond, header_default_vals)
            continue

        int_value = int(t['value'], 0)  # base 0 means check first two chars of t['value'] and decide
        binary_value = bin(int_value)[2:]  # binary value without `0b`
        per_field_binary_value = get_per_field_binary_value(binary_value, fields_used_in_transition_key, field_size_by_name)  # returns a [pair(field name, value)] for each field used in transition key

        new_cond = True
        for field_name, v in per_field_binary_value:
            v = "0b" + v
            bv = BitVecVal(int(v, 0), field_size_by_name[field_name])

            x, y = field_pos_by_name[field_name]
            assert y-1 >= x, "Wrong x y in new_cond creation"
            assert x >= 0, "x <= 0 in new_cond creation"
            new_cond = And(new_cond, Extract(y-1, x, z3_hdr) == bv)  # It is a concatenation of several Extract()==bv when using composite transition key

        next_st = t["next_state"]
        dfs(next_st, offset, headers, header_types, states, input, z3_result, len_, new_cond, header_default_vals)


def generate_z3_spec(p4, input, len_):
    all_parsers     = p4["parsers"]
    headers         = make_named_dict(p4["headers"])
    header_types    = make_named_dict(p4["header_types"])

    assert len(all_parsers) == 1, "Exactly 1 parser supported yet!"

    parser = all_parsers[0]
    states = make_named_dict(parser["parse_states"])

    curr = parser["init_state"]
    offset = 0
    z3_result = []

    # Create header_default_vals
    header_type_sizes = {}
    for t in header_types:
        s = 0
        for f in header_types[t]["fields"]: s += f[1]
        header_type_sizes[t] = s

    header_default_vals = {}
    for h in headers:
        s = header_type_sizes[headers[h]["header_type"]]
        if s: header_default_vals[headers[h]["name"]] = (BitVec(f'initial_val_{headers[h]["name"]}', s), s)

    dfs(curr, offset, headers, header_types, states, input, z3_result, len_, True, header_default_vals)

    return z3_result, header_default_vals


'''
input: a bitvec e.g., `input = BitVec('x', input_bit_stream_size)`
fielname: JSON file created out of a P4 program using `p4c <p4-program> -o <output_dir>
len_: len of input bitstream
'''
def read_json_and_generate_z3_spec(input, filename, len_):
    with open(filename) as file:
        p4 = json.load(file)

    return generate_z3_spec(p4, input, len_)