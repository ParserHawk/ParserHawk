#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

header mpls_t {
    bit<20> label;
    bit<3>  exp;
    bit<1>  bos;
    bit<8>  ttl;
}

header ipv4_t {
    bit<8>  f8;
}

header ipv6_t {
    bit<8>  f8;
}

header ethernet_t {
    bit<8>  f8;
}

struct headers {
    ipv4_t ipv4;
    ipv6_t ipv6;
    ethernet_t eth;
    mpls_t     mpls0;
    mpls_t     mpls1;
    mpls_t     mpls2;
}

struct metadata { 
}

// Skip egress
control BypassEgress(inout ingress_intrinsic_metadata_for_tm_t ig_tm_md) {
    apply {
    }
}

parser ParserI(packet_in b,
               out headers hdr,
               out metadata meta,
               out ingress_intrinsic_metadata_t ig_intr_md) {
    state start {
        transition parse_mpls0;
    }
    state parse_mpls0 {
        b.extract(hdr.mpls0);
        transition select(hdr.mpls0.bos) {
            1w0: parse_mpls1;
            1w1: parse_mpls_bos;
            default: accept;
        }
    }
    state parse_mpls1 {
        b.extract(hdr.mpls1);
        transition select(hdr.mpls1.bos) {
            1w0: parse_mpls2;
            1w1: parse_mpls_bos;
            default: accept;
        }
    }
    state parse_mpls2 {
        b.extract(hdr.mpls2);
        transition select(hdr.mpls2.bos) {
            1w0: parse_mpls2;
            1w1: parse_mpls_bos;
            default: accept;
        }
    }
    state parse_mpls_bos {
        transition select((b.lookahead<bit<4>>())[3:0]) {
            4w0x4: parse_mpls_inner_ipv4;
            4w0x6: parse_mpls_inner_ipv6;
            default: parse_eompls;
        }
    }
    state parse_mpls_inner_ipv4 {
        b.extract(hdr.ipv4);
        transition accept;
    }
    state parse_mpls_inner_ipv6 {
        b.extract(hdr.ipv6);
        transition accept;
    }
    state parse_eompls {
        b.extract(hdr.eth);
        transition accept;
    }
}

control IngressP(
        inout headers hdr,
        inout metadata meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_intr_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_intr_dprs_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_intr_tm_md) {
    apply { }
}

control DeparserI(
        packet_out b,
        inout headers hdr,
        in metadata meta,
        in ingress_intrinsic_metadata_for_deparser_t ig_intr_dprsr_md) {
    apply { b.emit(hdr.ipv4); }
}

parser ParserE(packet_in b,
               out headers hdr,
               out metadata meta,
               out egress_intrinsic_metadata_t eg_intr_md) {
    state start {
        transition accept;
    }
}
control EgressP(
        inout headers hdr,
        inout metadata meta,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_intr_prsr_md,
        inout egress_intrinsic_metadata_for_deparser_t ig_intr_dprs_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_intr_oport_md) {
    apply { }
}

control DeparserE(packet_out b,
                  inout headers hdr,
                  in metadata meta,
                  in egress_intrinsic_metadata_for_deparser_t ig_intr_dprs_md) {
    apply { b.emit(hdr.ipv4); }
}

Pipeline(ParserI(), IngressP(), DeparserI(), ParserE(), EgressP(), DeparserE()) pipe;
Switch(pipe) main;