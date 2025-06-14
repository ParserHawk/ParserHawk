header header_one {
    bit<8> type;
    bit<8> data;
}
header header_two {
    bit<8>  type;
    bit<16> data;
}
header header_four {
    bit<8>  type;
    bit<32> data;
}

struct Headers_t {
    header_one one;
    header_two two;
    header_four four;
}


state start {
        transition parse_headers;
    }

    state parse_headers {
        transition select(p.lookahead<bit<8>>()) {
            1: parse_one;
            2: parse_two;
            4: parse_four;
            default: accept;
        }
    }

    state parse_one {
        p.extract(headers.one);
        transition parse_headers;
    }
    state parse_two {
        p.extract(headers.two);
        transition parse_headers;
    }
    state parse_four {
        p.extract(headers.four);
        transition parse_headers;
    }