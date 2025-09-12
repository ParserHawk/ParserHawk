import random
from z3 import *

# -------- 配置 ----------
pkt_field_size_list = [4, 1]   # 举例，两个字段都是 4 bits
num_pkt_fields = len(pkt_field_size_list)
input_bit_stream_size = sum(pkt_field_size_list)

# -------- 函数 ----------
def specification(Input_bitstream, initial_field_val_list):
    O_field0 = Extract(input_bit_stream_size - 1,
                       input_bit_stream_size - pkt_field_size_list[0],
                       Input_bitstream)  # node 0
    Cond = Or(O_field0 == BitVecVal(12, 4), O_field0 == BitVecVal(0, 4))
    O_field1 = If(Cond,
                  Extract(input_bit_stream_size - 1 - pkt_field_size_list[0],
                          input_bit_stream_size - pkt_field_size_list[0] - pkt_field_size_list[1] + 1,
                          Input_bitstream),
                  BitVecVal(initial_field_val_list[1], pkt_field_size_list[1]))
    return [O_field0, O_field1]

def spec(Input_bitstream, initial_list):
    Fields = ["" for _ in range(num_pkt_fields)]
    Fields[0] = Input_bitstream[0 : pkt_field_size_list[0]]
    if int(Fields[0], 2) == 12 or int(Fields[0], 2) == 0:
        Fields[1] = Input_bitstream[pkt_field_size_list[0] : pkt_field_size_list[0] + pkt_field_size_list[1]]
    l = []
    for i in range(num_pkt_fields):
        if Fields[i] != "":
            l.append(int(Fields[i], 2))
        else:
            l.append(initial_list[i])
    return l

# -------- 测试 ----------
def test_equivalence(trials=10):
    for _ in range(trials):
        # 随机生成输入 bitstream (string)
        bits = "".join(random.choice("01") for _ in range(input_bit_stream_size))
        init_vals = [random.randint(0, (1 << pkt_field_size_list[i]) - 1) for i in range(num_pkt_fields)]

        # spec 结果
        res_concrete = spec(bits, init_vals)

        # specification 结果 (symbolic)
        bv = BitVecVal(int(bits, 2), input_bit_stream_size)
        res_sym = specification(bv, init_vals)

        s = Solver()
        if s.check() == sat:
            m = s.model()
            res_sym_eval = [m.eval(r).as_long() for r in res_sym]

            if res_sym_eval != res_concrete:
                print("Mismatch!")
                print("Bits:", bits)
                print("Init:", init_vals)
                print("spec:", res_concrete)
                print("specification:", res_sym_eval)
                return False
    print("All tests passed!")
    return True

if __name__ == "__main__":
    test_equivalence(20)
