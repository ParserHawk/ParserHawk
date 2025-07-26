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
    ipv6_t ipv6;
    arp_t arp;
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
      transition parse_packet_out_header;
  }
  state parse_packet_out_header {
    b.extract(hdr.packet_out_header);  // 1-bit
    transition parse_ethernet;
  }

  state parse_ethernet {
    b.extract(hdr.ethernet);   // 16-bit
    transition select(hdr.ethernet.ether_type) {
      0x0800: parse_ipv4; // 0x0800
      0x86dd: parse_ipv6; // 0x86dd
      0x0001: accept;
      0x0002: accept;
      0x0003: accept;
      0x0004: accept;
      0x0005: accept;
      0x0006: accept;
      0x0007: accept;
      0x0008: accept;
      0x0009: accept;
      0x000A: accept;
      0x000B: accept;
      0x000C: accept;
      0x000D: accept;
      0x000E: accept;
      0x000F: accept;
      0x0010: accept;
      0x0011: accept;
      0x0012: accept;
      0x0013: accept;
      0x0014: accept;
      0x0015: accept;
      0x0016: accept;
      0x0017: accept;
      0x0018: accept;
      0x0019: accept;
      0x001A: accept;
      0x001B: accept;
      0x001C: accept;
      0x001D: accept;
      0x001E: accept;
      0x001F: accept;
      0x0020: accept;
      0x0021: accept;
      0x0022: accept;
      0x0023: accept;
      0x0024: accept;
      0x0025: accept;
      0x0026: accept;
      0x0027: accept;
      0x0028: accept;
      0x0029: accept;
      0x002A: accept;
      0x002B: accept;
      0x002C: accept;
      0x002D: accept;
      0x002E: accept;
      0x002F: accept;
      0x0030: accept;
      0x0031: accept;
      0x0032: accept;
      0x0033: accept;
      0x0034: accept;
      0x0035: accept;
      0x0036: accept;
      0x0037: accept;
      0x0038: accept;
      0x0039: accept;
      0x003A: accept;
      0x003B: accept;
      0x003C: accept;
      0x003D: accept;
      0x003E: accept;
      0x003F: accept;
      0x0040: accept;
      0x0041: accept;
      0x0042: accept;
      0x0043: accept;
      0x0044: accept;
      0x0045: accept;
      0x0046: accept;
      0x0047: accept;
      0x0048: accept;
      0x0049: accept;
      0x004A: accept;
      0x004B: accept;
      0x004C: accept;
      0x004D: accept;
      0x004E: accept;
      0x004F: accept;
      0x0050: accept;
      0x0051: accept;
      0x0052: accept;
      0x0053: accept;
      0x0054: accept;
      0x0055: accept;
      0x0056: accept;
      0x0057: accept;
      0x0058: accept;
      0x0059: accept;
      0x005A: accept;
      0x005B: accept;
      0x005C: accept;
      0x005D: accept;
      0x005E: accept;
      0x005F: accept;
      0x0060: accept;
      0x0061: accept;
      0x0062: accept;
      0x0063: accept;
      0x0064: accept;
      0x0065: accept;
      0x0066: accept;
      0x0067: accept;
      0x0068: accept;
      0x0069: accept;
      0x006A: accept;
      0x006B: accept;
      0x006C: accept;
      0x006D: accept;
      0x006E: accept;
      0x006F: accept;
      0x0070: accept;
      0x0071: accept;
      0x0072: accept;
      0x0073: accept;
      0x0074: accept;
      0x0075: accept;
      0x0076: accept;
      0x0077: accept;
      0x0078: accept;
      0x0079: accept;
      0x007A: accept;
      0x007B: accept;
      0x007C: accept;
      0x007D: accept;
      0x007E: accept;
      0x007F: accept;
      0x0080: accept;
      0x0081: accept;
      0x0082: accept;
      0x0083: accept;
      0x0084: accept;
      0x0085: accept;
      0x0086: accept;
      0x0087: accept;
      0x0088: accept;
      0x0089: accept;
      0x008A: accept;
      0x008B: accept;
      0x008C: accept;
      0x008D: accept;
      0x008E: accept;
      0x008F: accept;
      0x0090: accept;
      0x0091: accept;
      0x0092: accept;
      0x0093: accept;
      0x0094: accept;
      0x0095: accept;
      0x0096: accept;
      0x0097: accept;
      0x0098: accept;
      0x0099: accept;
      0x009A: accept;
      0x009B: accept;
      0x009C: accept;
      0x009D: accept;
      0x009E: accept;
      0x009F: accept;
      0x00A0: accept;
      0x00A1: accept;
      0x00A2: accept;
      0x00A3: accept;
      0x00A4: accept;
      0x00A5: accept;
      0x00A6: accept;
      0x00A7: accept;
      0x00A8: accept;
      0x00A9: accept;
      0x00AA: accept;
      0x00AB: accept;
      0x00AC: accept;
      0x00AD: accept;
      0x00AE: accept;
      0x00AF: accept;
      0x00B0: accept;
      0x00B1: accept;
      0x00B2: accept;
      0x00B3: accept;
      0x00B4: accept;
      0x00B5: accept;
      0x00B6: accept;
      0x00B7: accept;
      0x00B8: accept;
      0x00B9: accept;
      0x00BA: accept;
      0x00BB: accept;
      0x00BC: accept;
      0x00BD: accept;
      0x00BE: accept;
      0x00BF: accept;
      0x00C0: accept;
      0x00C1: accept;
      0x00C2: accept;
      0x00C3: accept;
      0x00C4: accept;
      0x00C5: accept;
      0x00C6: accept;
      0x00C7: accept;
      0x00C8: accept;
      0x00C9: accept;
      0x00CA: accept;
      0x00CB: accept;
      0x00CC: accept;
      0x00CD: accept;
      0x00CE: accept;
      0x00CF: accept;
      0x00D0: accept;
      0x00D1: accept;
      0x00D2: accept;
      0x00D3: accept;
      0x00D4: accept;
      0x00D5: accept;
      0x00D6: accept;
      0x00D7: accept;
      0x00D8: accept;
      0x00D9: accept;
      0x00DA: accept;
      0x00DB: accept;
      0x00DC: accept;
      0x00DD: accept;
      0x00DE: accept;
      0x00DF: accept;
      0x00E0: accept;
      0x00E1: accept;
      0x00E2: accept;
      0x00E3: accept;
      0x00E4: accept;
      0x00E5: accept;
      0x00E6: accept;
      0x00E7: accept;
      0x00E8: accept;
      0x00E9: accept;
      0x00EA: accept;
      0x00EB: accept;
      0x00EC: accept;
      0x00ED: accept;
      0x00EE: accept;
      0x00EF: accept;
      0x00F0: accept;
      0x00F1: accept;
      0x00F2: accept;
      0x00F3: accept;
      0x00F4: accept;
      0x00F5: accept;
      0x00F6: accept;
      0x00F7: accept;
      0x00F8: accept;
      0x00F9: accept;
      0x00FA: accept;
      0x00FB: accept;
      0x00FC: accept;
      0x00FD: accept;
      0x00FE: accept;
      0x00FF: accept;
      0x0806:  parse_arp;  // 0x0806
      _:              accept;
    }
  }

  state parse_ipv4 {  
    b.extract(hdr.ipv4); // 1-bit
    transition accept;
  }

  state parse_ipv6 {
    b.extract(hdr.ipv6);  // 1-bit
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