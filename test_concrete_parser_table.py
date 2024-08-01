import unittest
from concrete_parser_table import *


def create_parser_table():
    parser_table = ParserTable(8)

    tcam_row = TcamRow('A', '*A', 'B', 3, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('A', '*B', 'C', 3, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('B', '*', 'accept', 1, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('C', '*', 'D', 2, '1')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('D', '11', 'E', 4, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('D', '01', 'F', 4, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('E', '*', 'accept', 5, '*')
    parser_table.tcam.append(tcam_row)

    tcam_row = TcamRow('F', '*', 'accept', 6, '*')
    parser_table.tcam.append(tcam_row)

    return parser_table

class TestParserOperation(unittest.TestCase):

    def test_parsing_1(self):
        parser_table = create_parser_table()
        parser = Parser('2AC1', parser_table)
        result = parser.execute()
        expected_value = 1
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_phv_1(self):
        parser_table = create_parser_table()
        parser = Parser('2AC1', parser_table)
        parser.execute()
        result = parser.packet_header_vector
        expected_value = ['2AC', '1']
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_parsing_2(self):
        parser_table = create_parser_table()
        parser = Parser('CCC1234', parser_table)
        result = parser.execute()
        expected_value = 0
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_phv_2(self):
        parser_table = create_parser_table()
        parser = Parser('CCC1234', parser_table)
        parser.execute()
        result = parser.packet_header_vector
        expected_value = ['CCC']
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_parsing_3(self):
        parser_table = create_parser_table()
        parser = Parser('2B671211ABCDE1', parser_table)
        result = parser.execute()
        expected_value = 1
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_phv_3(self):
        parser_table = create_parser_table()
        parser = Parser('2B671211ABCDE1', parser_table)
        parser.execute()
        result = parser.packet_header_vector
        expected_value = ['2B6', '71', '211A', 'BCDE1']
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_parsing_4(self):
        parser_table = create_parser_table()
        parser = Parser('2B6712017890123', parser_table)
        result = parser.execute()
        expected_value = 1
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_phv_4(self):
        parser_table = create_parser_table()
        parser = Parser('2B6712017890123', parser_table)
        parser.execute()
        result = parser.packet_header_vector
        expected_value = ['2B6', '71', '2017', '890123']
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_parsing_5(self):
        parser_table = create_parser_table()
        parser = Parser('2B671234ABCDEF12', parser_table)
        result = parser.execute()
        expected_value = 0
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value

    def test_phv_5(self):
        parser_table = create_parser_table()
        parser = Parser('2B671234ABCDEF12', parser_table)
        parser.execute()
        result = parser.packet_header_vector
        expected_value = ['2B6', '71', '234A']
        print("result:", result)
        print("expected_value:", expected_value)
        assert result == expected_value
    
if __name__ == '__main__':
    unittest.main()