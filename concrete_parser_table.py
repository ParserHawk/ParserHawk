# Use Figure 1 from Leapfrog as an example unit test.
# Specifically, Figure 1 can be used to generate an example parse table for testing.

import random

def ternary_match(pattern, data):
    # Check if lengths match or pattern is longer
    if len(pattern) != len(data):
        return False
    
    # Iterate through each character in pattern and data
    for p_char, d_char in zip(pattern, data):
        if p_char == '*':
            continue  # Wildcard matches any character
        if p_char != d_char:
            return False
    
    return True

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

        # for now, current_header would be sequential 1,2,3...
        # lookup_val is any random hexadecimal number between 0x1 and 0xA (i.e., a 4 bit match pattern)
        # next_header would be 2,3,4...
        # extract_len is any random number between 5 to 10 bytes
        # next_lookup_offset is any random number between 1 to 5 (to ensure legality for the random cases)
        # current granularity is 1 byte at a time.
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

    # Ensure rows are legal, i.e., next_lookup_offsets do not exceed extract_len of the next header.
    # Verification process would be possible after the entire table is populated, then we can run
    # a top down verification process, not possible to keep track when creating random tcam rows
    # Write a validation procedure to check if a parse table is legal
    def validate(self):
        offset_validity = None
        present_lookup_offset = self.tcam[0].next_lookup_offset
        for tcam_row_number in range(1, self.num_rows):
            if(present_lookup_offset > self.tcam[tcam_row_number].extract_len):
                return False
            present_lookup_offset = self.tcam[tcam_row_number].next_lookup_offset
        
        source_headers = []
        target_headers = []
        # Also check for if all target headers are present in the tcam table for lookup
        for tcam_entry in self.tcam:
            source_headers.append(tcam_entry.current_header)
            target_headers.append(tcam_entry.next_header)
        if(source_headers != target_headers):
            return False
        else:
            return True

    # display the parser table as row of dictionaries
    def __str__(self):
        result = []
        for row in self.tcam:
            result.append(str(vars(row)))
        return "\n".join(result)


class Parser:

    def __init__(self, t_bytestream, t_parser_table):
        self.bytestream = t_bytestream
        self.packet_header_vector = []
        self.parser_table = t_parser_table
        # self.parser_table.create_random_parse_table() # intialise a dummy parser table
        self.cursor = 0
        self.current_row = 0  # to keep track of which tcam row is being processed to finally end the parsing
        self.current_header_to_match = self.parser_table.tcam[0].current_header
        self.current_lookup_offset = 0

    def execute(self):

        # Do a while loop across the bytes in a bytestream until (1) either bytestream is exhausted, (2) failure state is reached, or (3) accept state is reached
        while self.cursor < len(self.bytestream):
            return_status = self.step()
            if not return_status: # no transitions present - parsing error
                return 0
            elif(return_status == 1): # transition was present, continue parsing
                self.cursor += self.parser_table.tcam[self.current_row].extract_len
            elif(return_status == 2): # parsing reached accept state
                return 1


    def step(self):


        for tcam_row_number in range(len(self.parser_table.tcam)):
            if(self.parser_table.tcam[tcam_row_number].current_header == self.current_header_to_match):
                # Assume extract happens before select, like in Figure 1 of the leapfrog paper.
                # Extract part of the bytestream starting from the current cursor position
                # But what if the parsing fails at the first state itself? Assuming the hdr_length is same in all transition entries for a specific header field
                bytestream_segment = self.bytestream[self.cursor : self.cursor + self.parser_table.tcam[tcam_row_number].extract_len]
                self.packet_header_vector.append(bytestream_segment)
                break

        # While or for loop across entries in TCAM table
        for tcam_row_number in range(len(self.parser_table.tcam)):
            if(self.parser_table.tcam[tcam_row_number].current_header == self.current_header_to_match):

                # Extract value from current header to match against the lookup_value
                # Match the lookup value with the bytestream portion starting from offset specified 
                # (a portion with same length as lookup_val - due to lack of end offset)
                to_lookup = '*'
                if(self.parser_table.tcam[tcam_row_number].lookup_val != '*'):
                    self.current_lookup_offset = int(self.current_lookup_offset)
                    to_lookup = bytestream_segment[self.current_lookup_offset : len(self.parser_table.tcam[tcam_row_number].lookup_val) + self.current_lookup_offset]

                if ternary_match(self.parser_table.tcam[tcam_row_number].lookup_val, to_lookup):
                    if(self.parser_table.tcam[tcam_row_number].next_header == 'accept'):
                        return 2 # to signify an accept state was reached
                    self.current_header_to_match = self.parser_table.tcam[tcam_row_number].next_header
                    self.current_lookup_offset = self.parser_table.tcam[tcam_row_number].next_lookup_offset
                    self.current_row = tcam_row_number
                    
                    # found a valid transition, parsing continues 
                    return 1
        
        # didn't find any matching lookups in the parse table after iterating through it => parsing fails
        return 0


if __name__ == '__main__':
    parser_table = ParserTable(5)
    parser_table.create_random_parse_table()
    print(parser_table)
    print(parser_table.validate())

    parser = Parser('0x1ABC97A', parser_table)
    match parser.execute():
        case 0: print("Parsing failed")
        case 1:
            print("Parsing succeeded")
            print(parser.packet_header_vector)

