
# Parses the transition key's value as json does some magic like bit shifting and bitwise AND to extract bits from fields
def parse_expression(expr, headers):
    if expr["type"] == "field":
        return (15, 0)

    elif expr["type"] == "expression":
        operation = expr["value"]["op"]

        if operation == ">>":
            # Right shift operation
            left = parse_expression(expr["value"]["left"])
            shift_amount = int(expr["value"]["right"]["value"], 16)  # in hex
            # Adjust the bit range by shifting to the right
            return (left[0] - shift_amount, left[1] - shift_amount)

        elif operation == "&":
            # AND operation with a mask
            left = parse_expression(expr["value"]["left"])
            right_value = int(expr["value"]["right"]["value"], 16)

            # Convert mask to binary and find bit positions that are set
            bin_mask = bin(right_value)[2:].zfill(16)  # 16-bit binary representation
            set_bits = [i for i, bit in enumerate(reversed(bin_mask)) if bit == '1']

            if set_bits:
                # Calculate range based on positions of set bits in the mask
                min_bit = min(set_bits)
                max_bit = max(set_bits)
                # Adjust the original range by applying the mask range
                return (left[1] + max_bit, left[1] + min_bit)

