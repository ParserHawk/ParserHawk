import json
import re

# generate a p4 program from z3's output in a json file
def codegen(json_obj, number_of_parser_nodes):
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
        # check flagij
        if v[0:4] == 'flag':
            nodeID = int(v[4])
            fieldID = int(v[5])
            if data[v] == 1:
                node_list[nodeID]["Extraction"] = "field_" + str(fieldID)
        # if field0_0 == i --> field0[0] is used as a key value in node i
        elif v[0:5] == 'field':
            pattern = r"field(\d+)_(\d+)"
            match = re.search(pattern, v)
            if match:
                # Extract the integer values
                bitID = int(match.group(2))
                fieldID = int(match.group(1))
                nodeID = int(data[v])
                if nodeID < number_of_parser_nodes:
                    if "Tran_key" not in node_list[nodeID]:
                        node_list[nodeID]["Tran_key"] = []
                    node_list[nodeID]["Tran_key"].append("field"+str(fieldID)+"["+str(bitID)+"]")
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
            pattern = r"tran_idx(\d+)_node(\d+)"
            match = re.search(pattern, v)
            # print("v =", v)
            if match:
                # Extract the integer values
                nodeID = int(match.group(2))
                tran_logicID = int(match.group(1))
                if "tran_logic" not in node_list[nodeID]:
                    node_list[nodeID]["tran_logic"] = []
                key_val_str = "key_val" + str(tran_logicID) + "_node" + str(nodeID)
                if key_val_str in data:
                    node_list[nodeID]["tran_logic"].append(["val:"+str(data[key_val_str]), "nxt:"+str(data[v])])
    print(node_list)
    
