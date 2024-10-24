from generate_spec import read_json_and_generate

def run(input, filename):
    result = read_json_and_generate(input, filename)
    for hdr in result:
        for field in hdr:
            print(f"{field} => {hdr[field]}")

def test1():
    filename = "tmp/simple_parser.json"
    print("--------- Start Test 1 ---------")
    input = "000000000000000010101010"  # 16 0s and 8 bits of alternating 1 and 0
    run(input, filename)
    print("--------- End Test 1 ---------")
    print("--------- Start Test 2 ---------")
    input = "000000000000000110101010"  # 15 0s and a 1 and then 8 bits of alterating 1 and 0
    run(input, filename)
    print("--------- End Test 2 ---------")

def test2():
    filename = "test/test.json"
    zero_width16 = "0000000000000000"
    one_width16 = "0000000000000001"
    two_width16 = "0000000000000010"

    zero_width8 = "00000000"
    one_width8 = "00000001"

    print("--------- Test (Expected: ethernet, ipv4, a) ---------")
    input = zero_width16 + zero_width8 + one_width8
    run(input, filename)

    print("--------- Test (Expected: ethernet, ipv6, b) ---------")
    input = one_width16 + zero_width16 + one_width8
    run(input, filename)

    print("--------- Test (Expected: ethernet) ---------")
    input = two_width16 + zero_width16 + one_width8
    run(input, filename)

    print("--------- Test (Expected: ethernet, ipv4, a, a, a) ---------")
    input = zero_width16 + zero_width8 + zero_width8 + zero_width8 + one_width8
    run(input, filename)

    print("--------- Test (Expected: ethernet, ipv6, b, b, b, b, b) ---------")
    input = one_width16 + zero_width16 + zero_width8 + zero_width8 + zero_width8 + zero_width8 + one_width8
    run(input, filename)


def main():
    # test1()
    test2()

if __name__ == "__main__":
    main()