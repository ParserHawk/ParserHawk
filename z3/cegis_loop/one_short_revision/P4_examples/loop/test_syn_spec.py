# ethernet_ip
# input_bit_stream_size = 16 + 25 + 1
# pkt_field_size_list = [16, 25, 8, 1]
# num_pkt_fields = len(pkt_field_size_list)

# def spec(Input_bitstream, initial_list):
#     # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
#     Fields = ["" for _ in range(num_pkt_fields)]
#     Fields[0] = Input_bitstream[0 : pkt_field_size_list[0]]
#     if Fields[0][0:16] == "0000100000000000":
#         Fields[1] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[1]]
#     elif Fields[0][0:16] == "1000011011011101":
#         Fields[2] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[2]]
#     # tcp
#     if Fields[0][0:16] == "0000100000000000" and Fields[1][0 : pkt_field_size_list[1]] == "0000000000000010100000110":
#         Fields[3] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[3]]
#     elif Fields[0][0:16] == "1000011011011101" and Fields[2][0:8] == "00000110": 
#         Fields[3] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[2] : pkt_field_size_list[0] + pkt_field_size_list[2] + pkt_field_size_list[3]]
#     # # udp
#     # if Fields[0][0:16] == "0000100000000000" and Fields[1][0 : pkt_field_size_list[1]] == "0000000000000010100010001":
#     #     Fields[4] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[4]]
#     # elif Fields[0][0:16] == "1000011011011101" and Fields[2][0:8] == "00010010": 
#     #     Fields[4] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[2] : pkt_field_size_list[0] + pkt_field_size_list[2] + pkt_field_size_list[4]]
#     # icmp
#     # if Fields[0][0:16] == "1000011011011101" and Fields[2][0:8] == "00111010": 
#     #     Fields[5] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[2] : pkt_field_size_list[0] + pkt_field_size_list[2] + pkt_field_size_list[5]]
#     l = []
#     for i in range(num_pkt_fields):
#         if Fields[i] != "":
#             l.append(int(Fields[i], 2))
#         else:
#             l.append(initial_list[i])
#     if int(Input_bitstream[0:16], 2) == 2048:
#         print("Input_bitstream[0:16] =", int(Input_bitstream[0:16], 2))
#         print("Input_bitstream[16:16+25] =", int(Input_bitstream[16:16+25], 2))
#         if int(Input_bitstream[16:16+25], 2) == 1286:
#             print("Input_bitstream[16+25] =", int(Input_bitstream[16+25], 2))
#     elif int(Input_bitstream[0:16], 2) == 34525:
#         print("Input_bitstream[0:16] =", int(Input_bitstream[0:16], 2))
#         print("Input_bitstream[16:16+8] =", int(Input_bitstream[16:16+8], 2))
#         if int(Input_bitstream[16:16+8], 2) == 6:
#             print("Input_bitstream[16+8] =", int(Input_bitstream[16+8], 2))
#     else:
#         print("Input_bitstream[0:16] =", int(Input_bitstream[0:16], 2))
#     # print("Input_bitstream[16+25] =", int(Input_bitstream[16+25], 2))
#     print("initial_list =", initial_list, "l =", l)
#     print("---------------")
#     return l

# # cexamples = [[0, 0, 0, 0, 0], [1179649, 0, 0, 0, 0], [1879441409, 0, 0, 0, 0], [35165044740, 0, 0, 32, 1], [51707514880, 0, 0, 0, 0], [68720525312, 0, 0, 0, 1], [69059223552, 0, 0, 0, 1], [137438956044, 0, 0, 1, 1], [137438956045, 0, 0, 1, 0], [137439346689, 0, 0, 0, 0], [137707651104, 0, 0, 0, 1], [138546249728, 0, 0, 0, 1], [172872564736, 0, 0, 1, 0], [2200365826049, 0, 0, 0, 0], [2200902434817, 0, 0, 16, 0], [2233651429378, 0, 0, 4, 1], [2316935233536, 0, 0, 0, 0]]
# cexamples = [[412381558131, 0, 0, 0, 0]]
# for j in range(len(cexamples)):
#     Input_bitval = cexamples[j][0]
#     random_initial_value_list = cexamples[j][1:]
#     spec(format(Input_bitval, '0{size}b'.format(size=input_bit_stream_size)), random_initial_value_list)

# loop
input_bit_stream_size = 6
# pkt_field_size_list = [16, 25, 8, 1, 1, 1]
pkt_field_size_list = [1, 1, 1, 1, 1]

num_pkt_fields = len(pkt_field_size_list)

# List the hardware configuration
lookahead_window_size = 2
size_of_key = 4

# parser_node_pipe = [1,2,3]
parser_node_pipe = [1,1,1,3]
num_parser_nodes = sum(parser_node_pipe)
# print("num_parser_nodes =", num_parser_nodes)
tcam_num = 3

def spec(Input_bitstream, initial_list):
    # l = [int(Input_bitstream[0 : 4], 2), int(Input_bitstream[4 : 8], 2)
    Fields = ["" for _ in range(num_pkt_fields)]
    Fields[0] = Input_bitstream[0 : pkt_field_size_list[0]]
    if Fields[0][0] == "0":
        Fields[1] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[1]]
        if Fields[1][0] == "1":
            if Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0100":
                Fields[2] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[2]]
            elif Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + 4] == "0110":
                Fields[3] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[3]]
            else:
                Fields[4] = Input_bitstream[pkt_field_size_list[0] + pkt_field_size_list[1] : pkt_field_size_list[0] + pkt_field_size_list[1] + pkt_field_size_list[4]]    
    else:
        if Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0100":
            Fields[2] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[2]]
        elif Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + 4] == "0110":
            Fields[3] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[3]]
        else:
            Fields[4] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[4]]
    l = []
    for i in range(num_pkt_fields):
        if Fields[i] != "":
            l.append(int(Fields[i], 2))
        else:
            l.append(initial_list[i])
    print("Input_bitstream =", Input_bitstream, "initial_list =", initial_list, "l =", l)
    return l

cexamples = [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 1], [10, 0, 1, 0, 0, 0], [20, 0, 0, 0, 1, 0], [20, 0, 0, 1, 0, 0], [22, 0, 0, 0, 1, 0], [24, 0, 0, 0, 0, 0], [40, 1, 0, 1, 0, 0]]
for j in range(len(cexamples)):
    Input_bitval = cexamples[j][0]
    random_initial_value_list = cexamples[j][1:]
    spec(format(Input_bitval, '0{size}b'.format(size=input_bit_stream_size)), random_initial_value_list)