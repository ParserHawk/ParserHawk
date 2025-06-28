#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

header ethernet_t {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16>         ether_type;
}
header dash_packet_meta_t {
    bit<8> packet_source;
    bit<4> packet_type;
    bit<4> packet_subtype;
    bit<16>     length;
}

header flow_key_t {
    bit<48> eni_mac;
    bit<16> vnet_id;
    bit<128> src_ip;
    bit<128> dst_ip;
    bit<16> src_port;
    bit<16> dst_port;
    bit<8> ip_proto;
    bit<7> reserved;
    bit<1> is_ip_v6;
}

struct headers {
    ethernet_t u0_ethernet;
    dash_packet_meta_t packet_meta;
    flow_key_t flow_key;
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
        packet.extract(hd.u0_ethernet);
        transition select(hd.u0_ethernet.ether_type) {
            // IPV4_ETHTYPE:  parse_u0_ipv4;  // 0x0800
            // IPV6_ETHTYPE:  parse_u0_ipv6;  // 0x86dd
            DASH_ETHTYPE:  parse_dash_hdr; // 0x876d
            default: accept;
        }
    }

    state parse_dash_hdr {
        packet.extract(hd.packet_meta);
        // FLOW_CREATE: 1, FLOW_UPDATE: 2, FLOW_DELETE: 3
        if (hd.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_CREATE
            || hd.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_UPDATE
            || hd.packet_meta.packet_subtype == dash_packet_subtype_t.FLOW_DELETE) {
            // Flow create/update/delete, extract flow_key
            packet.extract(hd.flow_key);
        }

        transition accept;
    }
    /*
    state parse_u0_ipv4 {
        packet.extract(hd.u0_ipv4);
        transition accept;
    }
    state parse_u0_ipv6 {
        packet.extract(hd.u0_ipv6);
        transition accept;
    }*/
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
    apply { b.emit(hdr.data); }
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
    apply { b.emit(hdr.data); }
}

Pipeline(ParserI(), IngressP(), DeparserI(), ParserE(), EgressP(), DeparserE()) pipe;
Switch(pipe) main;