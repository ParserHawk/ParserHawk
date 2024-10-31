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
def dfs(curr, offset, headers, header_types, states, input, z3_result, len):
    # Extract header from the curr state -- may contain multiple fields
    st = states[curr]
    assert len(st["parser_ops"]) == 1, "Exactly one op supported yet!"
    op = st["parser_ops"][0]
    assert op["op"] == "extract", "Only `extract` op support yet!"

    assert len(op["parameters"]) == 1, "Exactly one param supported yet!"
    param = op["parameters"][0]

    hdr_name = param["value"]
    hdr_type_info = header_types[headers[hdr_name]["header_type"]]
    fields = hdr_type_info["fields"]

    for f in fields:
        k = f"{hdr_name}.{f[0]}"
        z3_v = Extract(len - (offset+f[1]-1), len - offset, input)
        offset += f[1]

        tmp2 = {}
        tmp2[k] = z3_v
        z3_result += [tmp2]
    
    # get transition key
    assert len(st["transition_key"]) < 2, "Upto 1 transition key supported"
    transition_key_val = ""

    if (len(st["transition_key"])):
        transition_key_val = f'{st["transition_key"][0]["value"][0]}.{st["transition_key"][0]["value"][1]}'

    for t in st["transitions"]:
        assert t["mask"] == None, "Not accounting for mask right now"
        assert t["type"] in ["hexstr", "default"], f"Only hex type supported yet, found {t['type']}"

        if t["type"] == "default":
            next_st = t["next_state"]
            if next_st == None: continue
            dfs(next_st, offset, headers, header_types, states, input, z3_result, len)
            continue

        int_value = int(t["value"], 16)
        if int_value == int(''.join(vals), 2):
            next_st = t["next_state"]
            dfs(next_st, offset, headers, header_types, states, input, z3_result, len)

def generate_z3_spec(p4, input, len):
    all_parsers     = p4["parsers"]
    headers         = make_named_dict(p4["headers"])
    header_types    = make_named_dict(p4["header_types"])

    assert len(all_parsers) == 1, "Exactly 1 parser supported yet!"

    parser = all_parsers[0]
    states = make_named_dict(parser["parse_states"])

    curr = parser["init_state"]
    offset = 0
    result = []
    z3_result = []

    dfs(curr, offset, headers, header_types, states, input, result, z3_result, len)

    return result


def read_json_and_generate_z3_spec(input, filename, len):
    with open(filename) as file:
        p4 = json.load(file)

    return generate_z3_spec(p4, input, len)