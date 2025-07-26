#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

header data1_t {
    bit<16> f16;
}

header ipv4_t {
    bit<7> f7;
    bit<13> fragOffset;
    bit<4> ihl;
    bit<8> protocol;
}

header ipv6_t {
    bit<8> f8;
    bit<32> f32;
}

header tcp_t {
    bit<16> f16;
}

header udp_t {
    bit<32> f32;
}

header icmp_t {
    bit<8> f8;
}

struct headers {
    data1_t data1;
    ipv4_t   ipv4;
    ipv6_t   ipv6;
    tcp_t   tcp;
    udp_t   udp;
    icmp_t   icmp;
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
        transition ethernet;
    }
    state ethernet {
        b.extract(hdr.data1);
        transition select(hdr.data1.f16) {
            16w0x800: parse_ipv4;
            16w0x86dd: parse_ipv6;
            default: accept;
        }
    }
    state parse_ipv4 {
        b.extract(hdr.ipv4);
        transition select(hdr.ipv4.fragOffset, hdr.ipv4.ihl, hdr.ipv4.protocol) {
            // (13w0x0, 4w0x5, 8w0x1): parse_icmp;
            (13w0x0, 4w0x5, 8w0x6): parse_tcp;
            (13w0x0, 4w0x5, 8w0x11): parse_udp;
            // (13w0x0, 4w0x5, 8w0x2f): parse_gre;
            // (13w0x0, 4w0x5, 8w0x4): parse_ipv4_in_ip;
            // (13w0x0, 4w0x5, 8w0x29): parse_ipv6_in_ip;
            (13w0, 4w0, 8w2): parse_set_prio_med;
            (13w0, 4w0, 8w0x58 &&& 8w0xfe): parse_set_prio_med;
            // (13w0, 4w0, 8w89): parse_set_prio_med;
            (13w0, 4w0, 8w103): parse_set_prio_med;
            (13w0, 4w0, 8w112): parse_set_prio_med;
            default: accept;
        }
    }
    state parse_ipv6 {
        b.extract(hdr.ipv6);
        transition select(hdr.ipv6.f8) {
            8w58: parse_icmp;
            8w6: parse_tcp;
            // 8w4: parse_ipv4_in_ip;
            8w17: parse_udp;
            // 8w47: parse_gre;
            // 8w41: parse_ipv6_in_ip;
            8w0x58 &&& 8w0xfe: parse_set_prio_med;
            // 8w88: parse_set_prio_med;
            // 8w89: parse_set_prio_med;
            8w103: parse_set_prio_med;
            8w112: parse_set_prio_med;
            default: accept;
        }
    }
    state parse_icmp {
        b.extract(hdr.icmp);
        transition accept;
    }
    state parse_tcp {
        b.extract(hdr.tcp);
        transition accept;
    }
    state parse_udp {
        b.extract(hdr.udp);
        transition accept;
    }

    state parse_set_prio_med {
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
    apply { b.emit(hdr.data1); }
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
    apply { b.emit(hdr.data1); }
}

Pipeline(ParserI(), IngressP(), DeparserI(), ParserE(), EgressP(), DeparserE()) pipe;
Switch(pipe) main;