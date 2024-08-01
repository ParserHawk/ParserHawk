import unittest
from concrete_parser_table import *


def create_parser_table():
    parser_table = ParserTable(8)

    tcam_row = TcamRow(A, '0x2A', B, 3, _)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(A, '0x2B', C, 3, 1)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(B, _, *, 1, _)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(C, _, D, 2, 2)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(D, '0x11', E, 4, _)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(D, '0x01', F, 4, _)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(E, _, *, 5, _)
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow(F, _, *, 6, _)
    parser_table.tcam.append(tcam_row)

    return parser_table

class TestParserOperation(unittest.TestCase):

    def test1(self):
        pass

    def test2(self):
        pass
    
if __name__ == '__main__':
    unittest.main()