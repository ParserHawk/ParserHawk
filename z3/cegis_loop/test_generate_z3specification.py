from generate_spec import read_json_and_generate
from colorama import Fore, Style

zero_width16 = "0000000000000000"
one_width16 = "0000000000000001"
two_width16 = "0000000000000010"

zero_width8 = "00000000"
one_width8 = "00000001"

def run(input, filename):
    result = read_json_and_generate(input, filename)
    for hdr in result:
        for field in hdr:
            print(f"{field} => {hdr[field]}")
    return result

def verify(res, expected):
    assert len(res) == len(expected), f"{len(res)} != {len(expected)}"
    for hdr in res:
        assert hdr in expected
    print(Fore.GREEN + "Passed" + Style.RESET_ALL)

def test0():
    filename = "tmp/simple_parser.json"
    print("--------- Start Test 1 ---------")
    input = "000000000000000010101010"  # 16 0s and 8 bits of alternating 1 and 0
    run(input, filename)
    print("--------- End Test 1 ---------")
    print("--------- Start Test 2 ---------")
    input = "000000000000000110101010"  # 15 0s and a 1 and then 8 bits of alterating 1 and 0
    run(input, filename)
    print("--------- End Test 2 ---------")

def test():
    filename = "test/test.json"
    print(Fore.CYAN + f"============ Test {filename} ============" + Style.RESET_ALL)
    count = 0
    print("--------- Test (Expected: ethernet, ipv4, a) ---------")
    input = zero_width16 + zero_width8 + one_width8
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType": zero_width16},
        {"ipv4.version": zero_width8},
        {"a.val": one_width8},
    ])
    count += 1

    print("--------- Test (Expected: ethernet, ipv6, b) ---------")
    input = one_width16 + zero_width16 + one_width8
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType": one_width16},
        {"ipv6.version": zero_width16},
        {"b.wal": one_width8},
    ])
    count += 1

    print("--------- Test (Expected: ethernet) ---------")
    input = two_width16 + zero_width16 + one_width8
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType": two_width16},
    ])
    count += 1

    print("--------- Test (Expected: ethernet, ipv4, a, a, a) ---------")
    input = zero_width16 + zero_width8 + zero_width8 + zero_width8 + one_width8
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType": zero_width16},
        {"ipv4.version": zero_width8},
        {"a.val": zero_width8},
        {"a.val": zero_width8},
        {"a.val": one_width8},
    ])
    count += 1

    print("--------- Test (Expected: ethernet, ipv6, b, b, b, b, b) ---------")
    input = one_width16 + zero_width16 + zero_width8 + zero_width8 + zero_width8 + zero_width8 + one_width8
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType": one_width16},
        {"ipv6.version": zero_width16},
        {"b.wal": zero_width8},
        {"b.wal": zero_width8},
        {"b.wal": zero_width8},
        {"b.wal": zero_width8},
        {"b.wal": one_width8},
    ])
    count += 1
    print(Fore.GREEN + f"{count}/{count} Passed." + Style.RESET_ALL)

def test1():
    filename = "test2/test2.json"
    print(Fore.CYAN + f"============ Test {filename} ============" + Style.RESET_ALL)
    count = 0
    print("--------- Test (Expected: ethernet, ethernet) ---------")
    input = zero_width16 + one_width16 + zero_width16 + zero_width16
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType1": zero_width16},
        {"ethernet.etherType2": one_width16},
        {"ethernet.etherType1": zero_width16},
        {"ethernet.etherType2": zero_width16}
    ])
    count += 1

    print("--------- Test (Expected: ethernet) ---------")
    input = zero_width16 + zero_width16
    res = run(input, filename)
    verify(res, [
        {"ethernet.etherType1": zero_width16},
        {"ethernet.etherType2": zero_width16}
    ])
    count += 1

    print(Fore.GREEN + f"{count}/{count} Passed." + Style.RESET_ALL)

def main():
    test()
    test1()

if __name__ == "__main__":
    main()