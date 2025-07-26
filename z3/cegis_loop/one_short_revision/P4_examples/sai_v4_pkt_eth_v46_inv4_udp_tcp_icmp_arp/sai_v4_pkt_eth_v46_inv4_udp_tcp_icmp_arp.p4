#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

header packet_out_header_t {
  // The port this packet should egress out of.
  bit<32> egress_port;
  bit<2> submit_to_ingress;
  bit<6> unused_pad;
}

header ethernet_t {
  bit<48> dst_addr;
  bit<48> src_addr;
  bit<16> ether_type;
}

header ipv4_t {
  bit<4> version;
  bit<4> ihl;
  bit<6> dscp;  // The 6 most significant bits of the diff_serv field.
  bit<2> ecn;   // The 2 least significant bits of the diff_serv field.
  bit<16> total_len;
  bit<16> identification;
  bit<3> flags;
  bit<13> frag_offset;
  bit<8> ttl;
  bit<8> protocol;
  bit<16> header_checksum;
  bit<32> src_addr;
  bit<32> dst_addr;
}

header ipv6_t {
  bit<4> version;
  bit<6> dscp;  // The 6 most significant bits of the traffic_class field.
  bit<2> ecn;   // The 2 least significant bits of the traffic_class field.
  bit<20> flow_label;
  bit<16> payload_length;
  bit<8> next_header;
  bit<8> hop_limit;
  bit<128> src_addr;
  bit<128> dst_addr;
}

header udp_t {
  bit<16> src_port;
  bit<16> dst_port;
  bit<16> hdr_length;
  bit<16> checksum;
}

header tcp_t {
  bit<16> src_port;
  bit<16> dst_port;
  bit<32> seq_no;
  bit<32> ack_no;
  bit<4> data_offset;
  bit<4> res;
  bit<8> flags;
  bit<16> window;
  bit<16> checksum;
  bit<16> urgent_ptr;
}

header icmp_t {
  bit<8> type;
  bit<8> code;
  bit<16> checksum;
  bit<32> rest_of_header;
}

header arp_t {
  bit<16> hw_type;
  bit<16> proto_type;
  bit<8> hw_addr_len;
  bit<8> proto_addr_len;
  bit<16> opcode;
  bit<48> sender_hw_addr;
  bit<32> sender_proto_addr;
  bit<48> target_hw_addr;
  bit<32> target_proto_addr;
}

struct headers {
    packet_out_header_t packet_out_header;
    ethernet_t ethernet;
    ipv4_t ipv4;
    ipv4_t inner_ipv4;
    ipv6_t ipv6;
    arp_t arp;
    udp_t udp;
    tcp_t tcp;
    icmp_t icmp;
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
    b.extract(hdr.packet_out_header);  // 1-bit
    transition parse_ethernet;
  }

  state parse_ethernet {
    b.extract(hdr.ethernet);   // 16-bit
    transition select(hdr.ethernet.ether_type) {
      0x0800: parse_ipv4; // 0x0800
      0x86dd: parse_ipv6; // 0x86dd
      0x0806:  parse_arp;  // 0x0806
      _:              accept;
    }
  }

  state parse_ipv4 {  
    b.extract(hdr.ipv4); // 8-bit
    transition select(hdr.ipv4.protocol) {
      0x04: parse_ipv4_in_ip;
      0x11:  parse_udp;  // 0x11
      0x06:  parse_tcp;  // 0x06
      0x01: parse_icmp; // 0x01
      _:                accept;
    }
  }

  state parse_ipv6 {
    b.extract(hdr.ipv6);  // 8-bit
    transition select(hdr.ipv6.next_header) {
      0x3a: parse_icmp;  // 0x3a
      0x06:    parse_tcp; // 0x06
      0x11:    parse_udp; // 0x11
      _:                  accept;
    }
  }

  state parse_ipv4_in_ip {
    b.extract(hdr.inner_ipv4);  // 8-bit
    transition select(hdr.inner_ipv4.protocol) {
      0x11:  parse_udp;
      0x01: parse_icmp; 
      0x06:  parse_tcp;
      _:                accept;
    }
  }

  state parse_tcp {
    b.extract(hdr.tcp);  // 1-bit
    transition accept;
  }

  state parse_udp {
    b.extract(hdr.udp);  // 1-bit
    transition accept;
  }

  state parse_icmp {
    b.extract(hdr.icmp); // 1-bit
    transition accept;
  }

  state parse_arp {
    b.extract(hdr.arp);  // 1-bit
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
    apply { b.emit(hdr.packet_out_header); }
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
    apply { b.emit(hdr.packet_out_header); }
}

Pipeline(ParserI(), IngressP(), DeparserI(), ParserE(), EgressP(), DeparserE()) pipe;
Switch(pipe) main;

