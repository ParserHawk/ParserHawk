class TcamRow:
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
    def create_random_tcam_row():
        pass
        # TODO: Ensure rows are legal, i.e., next_lookup_offsets do not exceed extract_len of the next header.

class ParserTable:
    def __init__(self, NUM_ROWS):
        self.tcam = []
        for row_number in NUM_ROWS:
            current_row = TcamRow()
            self.tcam += current_row 
    def create_random_parse_table():
        pass
    def __str__(self):
        return "hello"

def Parser:
    def __init__(self):
        self.bitstring = ""
        self.packet_header_vector = []
        self.parser_table = ParserTable()
        self.cursor = -1 # how far within the bitstring have your progressed
    def execute(self):
        # input a bitstring, output a packet header vector
        # TODO: Implement the equivalent of Algorithm 1 and 2 from the Glen Gibb paper
        # Execute is a sequence of step() calls; each step corresponds to carrying out instructions from a single TCAM row
    def step(self):
        # TODO: Execute a single TCAM row

parser_table = ParserTable()
print(parser_table)
