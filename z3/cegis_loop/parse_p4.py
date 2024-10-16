import json

# Function to load and parse the JSON file
def parse_json_file(file_path):
    # key: struct name, val: {field_name: bit_size}
    field_dict = {}
    # key: parser state name, val: {"Extract":; "state_tran_key": "state_tran_rule":; "default":}
    parser_state_behavior_dict = {}
    try:
        # Open the JSON file
        with open(file_path, 'r') as json_file:
            # Load the JSON data
            data = json.load(json_file)
            assert data["Node_Type"] == "P4Program", "The node type should be P4Program"
            obj_dict = data["objects"]
            if obj_dict["Node_Type"] == "Vector<Node>":
                vec = obj_dict["vec"]
                for mem in vec:
                    # TODO: update the dict to record the bit size of each fields
                    if "Node_Type" in mem and mem["Node_Type"] == "Type_Header":
                        # print(mem)
                        name = mem["name"]
                        fields = mem["fields"]
                        field_list = fields["vec"]
                        field_dict[name] = {}
                        for k in field_list:
                            sub_field_name = k["name"]
                            type_dict = k["type"]
                            node_type = type_dict["Node_Type"]
                            if node_type == "Type_Bits":
                                node_size = type_dict["size"]
                                field_dict[name][sub_field_name] = node_size

                    # TODO: update the dict to record the parser info
                    elif "Node_Type" in mem and mem["Node_Type"] == "P4Parser":
                        states_dict = mem["states"]
                        parser_state_vec = states_dict["vec"]
                        for i in range(len(parser_state_vec)):
                            state_name = parser_state_vec[i]["name"]
                            if state_name == "accept" or state_name == "reject":
                                continue
                            parser_state_behavior_dict[state_name] = {}
                            parser_state_behavior_dict[state_name]["Extract"] = []
                            parser_state_behavior_dict[state_name]["state_tran_key"] = []
                            parser_state_behavior_dict[state_name]["state_tran_rule"] = {}
                            parser_state_behavior_dict[state_name]["default"] = None
                            # Get extraction
                            components = parser_state_vec[i]["components"]
                            components_vec = components["vec"]
                            for comp_dict in components_vec:
                                methodCall_dict = comp_dict["methodCall"]
                                method = methodCall_dict["method"]["member"]
                                if method == "extract":
                                    typeArguments = methodCall_dict["typeArguments"]
                                    arg_vec = typeArguments["vec"]
                                    for j in range(len(arg_vec)):
                                        var_type = arg_vec[j]["path"]["name"]
                                        parser_state_behavior_dict[state_name]["Extract"].append(var_type)
                                else:
                                    print("Does not support actions that are not extraction in parser nodes")
                                    exit(0)
                            # Get state transition
                            selectExpression = parser_state_vec[i]["selectExpression"]
                            #     print("selectExpression[select] =", selectExpression["select"])
                            # TODO: this might overfit to my test case
                            if "select" not in selectExpression:
                                # it means there is not select statement
                                path = selectExpression["path"]
                                next_node = path["name"]
                                parser_state_behavior_dict[state_name]["default"] = next_node
                            else:
                                # Get state transition key
                                select = selectExpression["select"]
                                components = select["components"]
                                components_vec = components["vec"]
                                for j in range(len(components_vec)):
                                    sub_field = components_vec[j]["member"]
                                    struct_name = components_vec[j]["expr"]["member"]
                                    parser_state_behavior_dict[state_name]["state_tran_key"].append(struct_name+"."+sub_field)


                                selectCases = selectExpression["selectCases"]
                                selectCases_vec = selectCases["vec"]
                                for j in range(len(selectCases_vec)):
                                    assert selectCases_vec[j]["Node_Type"] == "SelectCase", "Node in select case should have the type SelectCase"
                                    keyset = selectCases_vec[j]["keyset"]
                                    if keyset["Node_Type"] == "Constant":
                                        match_val = keyset["value"]
                                        base = keyset["base"]
                                        # get the nxt parser node name
                                        state = selectCases_vec[j]["state"]
                                        nxt_node_name = state["path"]["name"]
                                        parser_state_behavior_dict[state_name]["state_tran_rule"][int(str(match_val), base)] = nxt_node_name
                                    elif keyset["Node_Type"] == "DefaultExpression":
                                        state = selectCases_vec[j]["state"]
                                        nxt_node_name = state["path"]["name"]
                                        parser_state_behavior_dict[state_name]["default"] = nxt_node_name


    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {file_path}")
    
    pretty_json = json.dumps(parser_state_behavior_dict, indent=4)
    print(pretty_json)
# Example usage:
if __name__ == "__main__":
    # Provide the path to your JSON file
    json_file_path = '/tmp/out.json'
    
    # Call the parsing function
    parse_json_file(json_file_path)
