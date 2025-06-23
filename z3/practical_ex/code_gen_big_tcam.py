from jinja2 import Environment, FileSystemLoader
import os
import json
import re

# def node0(Fields, I, pos, idx):
#     if idx != 0:
#         return Fields, pos, idx
#     Fields[0] = I[pos : pos + 8]
#     # print("Fields[0][4:8] =", Fields[0][4:8])
#     if Fields[0][4 : 4 + 4] == bitarray('1111'):
#         next_idx = 1
#     elif Fields[0][4 : 4 + 4] == bitarray('0011'):
#         next_idx = 2
#     else:
#         next_idx = 3
#     return Fields, pos + 8, next_idx
def get_impl_python(node_list):
    ret_python = ""
    for i in range(len(node_list)):
        curr_dict = node_list[i]
        ret_python += f"""
def node{i}(Fields, I, pos, idx):
    if idx != {i}:
        return Fields, pos, idx
"""
        if curr_dict["Extraction"] != None: 
            pattern = r'field_(\d+)'
            match = re.search(pattern, curr_dict["Extraction"])
            fieldID = int(match.group(1))
            ret_python += f"""
Fields[{fieldID}] = I[pos : pos + 8]
"""
    return ret_python

"""e.g., field0[7] < field0[0], field1[0] > field0[0]"""
def custom_sort(arr):
    n = len(arr)
    
    # Bubble sort
    for i in range(n):
        for j in range(0, n - i - 1):
            # Using the custom comparison function
            pattern = r'field(\d+)\[(\d+)\]'
            matchfirst = re.search(pattern, arr[j]) # 0 7
            matchsecond = re.search(pattern, arr[j + 1]) # 1 0
            if matchfirst and matchsecond:
                if matchfirst.group(1) > matchsecond.group(1) or (matchfirst.group(1) == matchsecond.group(1) and matchfirst.group(2) < matchsecond.group(2)):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
            elif matchsecond:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def generate_impl(node_list):
    # [{'Extraction': 'field_0', 'Tran_key': ['field0[2]', 'field1[2]'], 'default_tran': 2, 'tran_logic': []}, {'Extraction': 'field_1', 'Tran_key': ['field0[0]', 'field0[1]', 'field0[3]', 'field1[0]', 'field1[1]'], 'default_tran': None, 'tran_logic': []}]
    num_parser_node = len(node_list)
    python_str = ""
    l = [8,4,6]
    for i in range(num_parser_node):
        parser_node_dict = num_parser_node[i]
        
        python_str += "def node{node}(Fields, I, pos, idx):\n".format(node = i)
        python_str +=  "if idx != {node}: \n \t\treturn Fields, pos, idx\n".format(node = i)
        # Extraction
        extract_field = parser_node_dict['Extraction']
        forward = 0
        if extract_field != None:
            pattern = r"field(\d+)"
            match = re.search(pattern, extract_field)
            fieldID = int(match.group(1))
            # Fields[0] = I[pos : pos + 8]
            python_str += "Fields[{fieldID}] = I[pos : pos + {fieldSize}]\n".format(fieldID = fieldID, fieldSize = l[fieldID])
            forward = l[fieldID]
        # Key generation
        # TODO: pass size_of_key = 2 as a parameter
        size_of_key = 2
        Tran_key = parser_node_dict['Tran_key'][-size_of_key :]
        # State_transition
        Tran_logic = parser_node_dict['tran_logic']
        default_tran = parser_node_dict['default_tran']
        for i in range(len(Tran_logic)):
            if i == 0:
                python_str += "if Fields[0][4 : 4 + 4] == bitarray('1111'):\n"
                python_str += "next_idx = {next_idx}".format(next_idx = Tran_logic[i][1])
            else:
                python_str += "elif Fields[0][4 : 4 + 4] == bitarray('1111'):\n"
                python_str += "next_idx = {next_idx}\n".format(next_idx = Tran_logic[i][1])
        if default_tran != None:
            python_str += "else:\n"
            python_str += "next_idx = {next_idx}\n".format(next_idx = default_tran)
        #     if Fields[0][4 : 4 + 4] == bitarray('1111'):
        #         next_idx = 1
        #     elif Fields[0][4 : 4 + 4] == bitarray('0011'):
        #         next_idx = 2
        #     else:
        #         next_idx = 3
        
        #     return Fields, pos + 8, next_idx
        python_str += "return Fields, pos + {fieldSize}, next_idx\n".format(fieldSize = forward)
        
    return None

# generate a p4 program from z3's output in a json file
def codegen(json_obj, number_of_parser_nodes, size_of_key):
    print("From codegen function")
    node_list = []
    # print(json_obj)
    for i in range(number_of_parser_nodes):
        node_list.append({})
        node_list[i]["Extraction"] = None
        node_list[i]["Tran_key"] = []
        node_list[i]["default_tran"] = None
        node_list[i]["tran_logic"] = []
    data = json.loads(json_obj)
    sorted_keys = sorted(data.keys())
    for v in sorted_keys:
        # check flag_i_j
        if v[0:4] == 'flag':
            pattern = r'^flag_(\d+)_(\d+)$'
            match = re.match(pattern, v)
            nodeID = match.group(1)
            fieldID = match.group(2)
            if data[v] == 1:
                node_list[int(nodeID)]["Extraction"] = "field_" + str(fieldID)
        # if field0_0 == i --> field0[0] is used as a key value in node i
        elif v[0:5] == 'field':
            pattern = r"field(\d+)_(\d+)"
            match = re.search(pattern, v)
            if match:
                # Extract the integer values
                bitID = int(match.group(2))
                fieldID = int(match.group(1))
                nodeID = int(data[v])
                if v.find('post') == -1:
                    if nodeID < number_of_parser_nodes:
                        if "Tran_key" not in node_list[nodeID]:
                            node_list[nodeID]["Tran_key"] = []
                        node_list[nodeID]["Tran_key"].append("field"+str(fieldID)+"["+str(bitID)+"]")
                else:
                    if nodeID < number_of_parser_nodes:
                        if "Tran_key" not in node_list[nodeID]:
                            node_list[nodeID]["Tran_key"] = []
                        node_list[nodeID]["Tran_key"].append("post process field"+str(fieldID)+"["+str(bitID)+"]")
        # key_val0_node0
        # tran_idx0_node0
        # default_idx_node0
        elif v[0:16] == "default_idx_node":
            pattern = r"default_idx_node(\d+)"
            match = re.search(pattern, v)
            if match:
                nodeID = int(match.group(1))
                node_list[nodeID]["default_tran"] = data[v]
        elif v[0:8] == "tran_idx":
            pattern = r"tran_idx(\d+)"
            match = re.search(pattern, v)
            # print("v =", v)
            if match:
                # Extract the integer values
                tran_logicID = int(match.group(1))
                
                assign_val_str = "assign_" + str(tran_logicID)
                key_val_str = "key_val" + str(tran_logicID)
                key_mask_str = "key_mask" + str(tran_logicID)
                if assign_val_str in data and key_mask_str in data and key_val_str in data:
                    print(f"{assign_val_str} =".format(assign_val_str), data[assign_val_str], 
                          f"{key_val_str} =".format(key_val_str), data[key_val_str], f"{key_mask_str} =".format(key_mask_str), data[key_mask_str], 
                          f"{v} =".format(v), data[v])
                    nodeID = int(data[assign_val_str])
                    if nodeID < number_of_parser_nodes:
                        if "tran_logic" not in node_list[nodeID]:
                            node_list[nodeID]["tran_logic"] = []
                        node_list[nodeID]["tran_logic"].append(["val:"+str(data[key_val_str]), "mask:"+str(data[key_mask_str]), "nxt:"+str(data[v])])
                # elif key_val_str in data:
                #     node_list[nodeID]["tran_logic"].append(["val:"+str(data[key_val_str]), "nxt:"+str(data[v])])
        elif v.find("ahead") != -1:
            pattern = r"node(\d+)_ahead(\d+)"
            match = re.search(pattern, v)
            if data[v] != 1:
                continue
            # print("match =", match)
            if match: 
                nodeID = int(match.group(1))
                aheadBit = int(match.group(2))
                # print("nodeID =", nodeID, "aheadBit =", aheadBit)
                if "Tran_key" not in node_list[nodeID]:
                    node_list[nodeID]["Tran_key"] = []
                node_list[nodeID]["Tran_key"].append("lookahead" + " "+str(aheadBit)+" ")
                # print("Come here")
    for i in range(number_of_parser_nodes):
        if len(node_list[i]['Tran_key']) != 0:
            node_list[i]['Tran_key'] = custom_sort(node_list[i]['Tran_key'])
            # if len(node_list[i]['Tran_key']) > size_of_key:
            #     node_list[i]['Tran_key'] = node_list[i]['Tran_key'][-size_of_key : ]
    
    # TODO: generate the impl python file
    # python_gen_str = get_impl_python(node_list=node_list)
    # print("python_gen_str =", python_gen_str)

    # Convert list of dict to JSON string
    json_string = json.dumps(node_list, indent=4)

    # Print the JSON string
    # print(json_string)
    # Write JSON to a file
    return json_string
    
