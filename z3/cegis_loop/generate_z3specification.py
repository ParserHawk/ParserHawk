import json
from z3 import BitVec, Extract, If, And, BitVecVal

'''
Makes it easy to access data by name
'''
def make_named_dict(data):
    res = {}
    for d in data:
        res[d["name"]] = d
    return res

'''
DFS: Extracts field from a state and transitions to the next state
'''
def dfs(curr, offset, headers, header_types, states, input, z3_result, len_, cond, initial_field_val_list, global_index):
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

    assert len(fields) == 1, "1 field per header support yet"

    f = fields[0]
    k = f"{hdr_name}.{f[0]}"

    hi = (len_ - offset) - 1
    lo = (len_ - (offset + f[1] - 1)) - 1
    z3_field = If(cond, Extract(hi, lo, input), initial_field_val_list[global_index])  # constructing z3 expression

    offset += f[1]
    z3_result += [{k: z3_field}]

    # get transition key
    assert len(st["transition_key"]) < 2, "Upto 1 transition key supported"

    transition_key_val = ""
    transition_key_val_size = 0

    if (len(st["transition_key"])):
        h_ = st["transition_key"][0]["value"][0]
        f_ = st["transition_key"][0]["value"][1]
        transition_key_val = f'{h_}.{f_}'  # for example, "value" : ["ethernet", "etherType"]

        # Get the size
        for elem in header_types[headers[h_]["header_type"]]["fields"]:
            if elem[0] == f_:
                transition_key_val_size = elem[1]
                break

    for t in st["transitions"]:
        assert t["mask"] == None, "Not accounting for mask right now"
        assert t["type"] in ["hexstr", "default"], f"Only hex type supported yet, found {t['type']}"

        global_index += 1

        if t["type"] == "default":
            next_st = t["next_state"]
            if next_st == None: continue
            new_cond = True
            dfs(next_st, offset, headers, header_types, states, input, z3_result, len_, new_cond, initial_field_val_list, global_index)
            continue

        int_value = int(t['value'], 16)
        bv = BitVecVal(int_value, 4*(len(t['value'])-2))  # json shows values as hex, we convert it into binary and calculate len of binary value accordingly: substract 2 for `0x` and then 4x

        # TODO: Make it generic now. Matching key can be a subset of the header bits, not necessarily the enture header/field
        hi = transition_key_val_size-1
        lo = 0

        matching_key = Extract(hi, lo, z3_field)
        new_cond = matching_key == bv
        next_st = t["next_state"]
        dfs(next_st, offset, headers, header_types, states, input, z3_result, len_, new_cond, initial_field_val_list, global_index)


def generate_z3_spec(p4, input, len_, initial_field_val_list):
    all_parsers     = p4["parsers"]
    headers         = make_named_dict(p4["headers"])
    header_types    = make_named_dict(p4["header_types"])

    assert len(all_parsers) == 1, "Exactly 1 parser supported yet!"

    parser = all_parsers[0]
    states = make_named_dict(parser["parse_states"])

    curr = parser["init_state"]
    offset = 0
    z3_result = []

    dfs(curr, offset, headers, header_types, states, input, z3_result, len_, True, initial_field_val_list, 0)

    return z3_result


'''
input: a bitvec e.g., `input = BitVec('x', input_bit_stream_size)`
fielname: JSON file created out of a P4 program using `p4c <p4-program> -o <output_dir>
len_: len of input bitstream
initial_field_val_list: just random list of size len_ for now
'''
def read_json_and_generate_z3_spec(input, filename, len_, initial_field_val_list):
    with open(filename) as file:
        p4 = json.load(file)

    return generate_z3_spec(p4, input, len_, initial_field_val_list)