import json

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
def dfs(curr, offset, parser, headers, header_types, states, input, result):
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

    res = {}
    for f in fields:
        res[f"{hdr_name}.{f[0]}"] = input[offset:offset+f[1]]
        offset += f[1]
    
    result += [res]

    # Handle transitions from curr state and recurse
    assert len(st["transition_key"]) <= 1, "Upto 1 transition keys supported"
    key = None
    if len(st["transition_key"]) > 0:
        transition_key_val = st["transition_key"][0]["value"]
        key = f"{transition_key_val[0]}.{transition_key_val[1]}"

    for t in st["transitions"]:
        assert t["mask"] == None, "Not accounting for mask right now"
        assert t["type"] in ["hexstr", "default"], f"Only hex type supported yet, found {t['type']}"

        if t["type"] == "default":
            next_st = t["next_state"]
            if next_st == None: continue
            dfs(next_st, offset, parser, headers, header_types, states, input, result)
            continue

        assert key != None, "A non default state found, but no transition key was found"
        int_value = int(t["value"], 16)
        if int_value == int(res[key], 2):
            next_st = t["next_state"]
            dfs(next_st, offset, parser, headers, header_types, states, input, result)
            continue  # Only one match can happen, right?

def generate(p4, input):
    all_parsers     = p4["parsers"]
    headers         = make_named_dict(p4["headers"])
    header_types    = make_named_dict(p4["header_types"])

    assert len(all_parsers) == 1, "Exactly 1 parser supported yet!"

    parser = all_parsers[0]
    states = make_named_dict(parser["parse_states"])

    curr = parser["init_state"]
    offset = 0
    result = []

    dfs(curr, offset, parser, headers, header_types, states, input, result)

    return result


def read_json_and_generate(input, filename):
    with open(filename) as file:
        p4 = json.load(file)

    return generate(p4, input)