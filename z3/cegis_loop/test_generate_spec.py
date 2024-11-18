import sys
from generate_spec import read_json_and_generate
from colorama import Fore, Style

zero_width16 = "0000000000000000"
sixteen_ones = "1111111111111111"
one_width16 = "0000000000000001"
two_width16 = "0000000000000010"

zero_width8 = "00000000"
one_width8 = "00000001"

def run(input, filename):
    if len(sys.argv) > 1: filename = sys.argv[1]
    result = read_json_and_generate(input, filename)
    for record in result:
        for hdr in record:
            print(hdr, "=>", record[hdr])
    return result

def verify(res, expected):
    print(res)
    print(expected)
    assert len(res) == len(expected), f"{len(res)} != {len(expected)}"
    for hdr in res:
        assert hdr in expected
    print(Fore.GREEN + "Passed" + Style.RESET_ALL)


def test_xg():
    filename = "xg_example1/xg.json"
    input = sixteen_ones + sixteen_ones + "1"
    for i in range(0, 31):
        input += "0"

    for i in range(0, 112):
        input += "0"

    res = run(input, filename)

def test_xg2():
    filename = "xg_example2/xg2.json"
    input = sixteen_ones + sixteen_ones + "1"
    for i in range(0, 31):
        input += "0"

    for i in range(0, 112):
        input += "0"

    res = run(input, filename)

def main():
    test_xg()
    # test_xg2()

if __name__ == "__main__":
    main()