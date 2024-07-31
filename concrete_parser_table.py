import random

class TcamRow:

    # class variable to keep track of number of tcam rows generated
    current_header_counter = 1

    def __init__(self, t_current_header, t_lookup_val, t_next_header, t_extract_len, t_next_lookup_offset):
        self.current_header     = t_current_header
        self.lookup_val         = t_lookup_val
        self.next_header        = t_next_header
        self.extract_len        = t_extract_len
        # same as hdr_len in the Gibb et al. ANCS 2012 paper,
        # refers to how long the current header in bytes is,
        # and hence how much should be deposited into the packet_header_vector and also
        # how much the cursor should be advanced by
        self.next_lookup_offset = t_next_lookup_offset 

    @classmethod
    def create_random_tcam_row(cls):
        # TODO: Ensure rows are legal, i.e., next_lookup_offsets do not exceed extract_len of the next header.
        # Verification process would be possible after the entire table is populated, then we can run
        # a top down verification process, not possible to keep track when creating random tcam rows

        # for now, current_header would be sequential 1,2,3...
        # lookup_val is any random hexadecimal number between 0x1 and 0xA
        # next_header would be 2,3,4...
        # extract_len is any random number between 5 to 10
        # next_lookup_offset is any random number between 1 to 5 (to ensure legality for the random cases)

        t_current_header = cls.current_header_counter
        t_lookup_val = hex(random.randint(0x1, 0xA))
        t_next_header = cls.current_header_counter + 1
        t_extract_len = random.randint(5, 10)
        t_next_lookup_offset = random.randint(1, 5)
        
        # Increment the counter for the next row
        cls.current_header_counter += 1
        
        return cls(t_current_header, t_lookup_val, t_next_header, t_extract_len, t_next_lookup_offset)


class ParserTable:
    def __init__(self, t_num_rows):
        self.tcam = []
        self.num_rows = t_num_rows

    # create a new random parse table by repeatedly calling the random tcam row generator t_num_rows times
    def create_random_parse_table(self):
        for _ in range(self.num_rows):
            self.tcam.append(TcamRow.create_random_tcam_row())

    # display the parser table as row of dictionaries
    def __str__(self):
        result = []
        for row in self.tcam:
            result.append(str(vars(row)))
        return "\n".join(result)


class Parser:
    def __init__(self, t_bitstring):
        self.bitstring = t_bitstring
        self.packet_header_vector = []
        self.parser_table = ParserTable(5)
        self.parser_table.create_random_parse_table() # intialise a dummy parser table
        self.cursor = 0
        self.current_row = 0  # to keep track of which tcam row is being processed to finally end the parsing

    def execute(self):
        # Logic for now is if parsing fails to go through all tcam entries, it is a failure, otherwise it succeeds
        while self.current_row < len(self.parser_table.tcam):
            if not self.step():
                print("Parsing failed")
                return
        print("Parsing success")
        print("Packet Header Vector:", self.packet_header_vector)

    def step(self):
        row = self.parser_table.tcam[self.current_row]
        
        # Extract part of the bitstring starting from the current cursor position
        bitstring_segment = self.bitstring[self.cursor:self.cursor + row.extract_len]

        # Extract value from current header to match against the lookup_value
        to_lookup = bitstring_segment[row.next_lookup_offset: len(row.lookup_val) + row.next_lookup_offset]
        
        # Match the lookup value with the bitstring portion starting from offset specified 
        # (a portion with same length as lookup_val - due to lack of end offset)
        if to_lookup == row.lookup_val:
            self.packet_header_vector.append(bitstring_segment)
            self.cursor += row.extract_len
            self.current_row += 1
            return True
        else:
            return False
        

parser_table = ParserTable(5)
parser_table.create_random_parse_table()
print(parser_table)

parser = Parser('110101001010110011')
parser.execute()