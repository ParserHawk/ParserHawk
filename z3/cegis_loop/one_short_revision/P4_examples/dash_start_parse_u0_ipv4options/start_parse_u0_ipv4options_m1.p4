#include <core.p4>
#if __TARGET_TOFINO__ == 3
#include <t3na.p4>
#elif __TARGET_TOFINO__ == 2
#include <t2na.p4>
#else
#include <tna.p4>
#endif

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
header ipv4options_t {
    varbit<320> options;
}

struct headers {
    ipv4_t u0_ipv4;
    ipv4options_t u0_ipv4options;
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
        b.extract(hdr.u0_ipv4);
        transition select (hdr.u0_ipv4.ihl) {
                5: accept;
                0x0000: parse_u0_ipv4options;
                0x0001: parse_u0_ipv4options;
                0x0002: parse_u0_ipv4options;
                0x0003: parse_u0_ipv4options;
                0x0004: parse_u0_ipv4options;
                0x0005: parse_u0_ipv4options;
                0x0006: parse_u0_ipv4options;
                0x0007: parse_u0_ipv4options;
                0x0008: parse_u0_ipv4options;
                0x0009: parse_u0_ipv4options;
                0x000A: parse_u0_ipv4options;
                0x000B: parse_u0_ipv4options;
                0x000C: parse_u0_ipv4options;
                0x000D: parse_u0_ipv4options;
                0x000E: parse_u0_ipv4options;
                0x000F: parse_u0_ipv4options;
                0x0010: parse_u0_ipv4options;
                0x0011: parse_u0_ipv4options;
                0x0012: parse_u0_ipv4options;
                0x0013: parse_u0_ipv4options;
                0x0014: parse_u0_ipv4options;
                0x0015: parse_u0_ipv4options;
                0x0016: parse_u0_ipv4options;
                0x0017: parse_u0_ipv4options;
                0x0018: parse_u0_ipv4options;
                0x0019: parse_u0_ipv4options;
                0x001A: parse_u0_ipv4options;
                0x001B: parse_u0_ipv4options;
                0x001C: parse_u0_ipv4options;
                0x001D: parse_u0_ipv4options;
                0x001E: parse_u0_ipv4options;
                0x001F: parse_u0_ipv4options;
                0x0020: parse_u0_ipv4options;
                0x0021: parse_u0_ipv4options;
                0x0022: parse_u0_ipv4options;
                0x0023: parse_u0_ipv4options;
                0x0024: parse_u0_ipv4options;
                0x0025: parse_u0_ipv4options;
                0x0026: parse_u0_ipv4options;
                0x0027: parse_u0_ipv4options;
                0x0028: parse_u0_ipv4options;
                0x0029: parse_u0_ipv4options;
                0x002A: parse_u0_ipv4options;
                0x002B: parse_u0_ipv4options;
                0x002C: parse_u0_ipv4options;
                0x002D: parse_u0_ipv4options;
                0x002E: parse_u0_ipv4options;
                0x002F: parse_u0_ipv4options;
                0x0030: parse_u0_ipv4options;
                0x0031: parse_u0_ipv4options;
                0x0032: parse_u0_ipv4options;
                0x0033: parse_u0_ipv4options;
                0x0034: parse_u0_ipv4options;
                0x0035: parse_u0_ipv4options;
                0x0036: parse_u0_ipv4options;
                0x0037: parse_u0_ipv4options;
                0x0038: parse_u0_ipv4options;
                0x0039: parse_u0_ipv4options;
                0x003A: parse_u0_ipv4options;
                0x003B: parse_u0_ipv4options;
                0x003C: parse_u0_ipv4options;
                0x003D: parse_u0_ipv4options;
                0x003E: parse_u0_ipv4options;
                0x003F: parse_u0_ipv4options;
                0x0040: parse_u0_ipv4options;
                0x0041: parse_u0_ipv4options;
                0x0042: parse_u0_ipv4options;
                0x0043: parse_u0_ipv4options;
                0x0044: parse_u0_ipv4options;
                0x0045: parse_u0_ipv4options;
                0x0046: parse_u0_ipv4options;
                0x0047: parse_u0_ipv4options;
                0x0048: parse_u0_ipv4options;
                0x0049: parse_u0_ipv4options;
                0x004A: parse_u0_ipv4options;
                0x004B: parse_u0_ipv4options;
                0x004C: parse_u0_ipv4options;
                0x004D: parse_u0_ipv4options;
                0x004E: parse_u0_ipv4options;
                0x004F: parse_u0_ipv4options;
                0x0050: parse_u0_ipv4options;
                0x0051: parse_u0_ipv4options;
                0x0052: parse_u0_ipv4options;
                0x0053: parse_u0_ipv4options;
                0x0054: parse_u0_ipv4options;
                0x0055: parse_u0_ipv4options;
                0x0056: parse_u0_ipv4options;
                0x0057: parse_u0_ipv4options;
                0x0058: parse_u0_ipv4options;
                0x0059: parse_u0_ipv4options;
                0x005A: parse_u0_ipv4options;
                0x005B: parse_u0_ipv4options;
                0x005C: parse_u0_ipv4options;
                0x005D: parse_u0_ipv4options;
                0x005E: parse_u0_ipv4options;
                0x005F: parse_u0_ipv4options;
                0x0060: parse_u0_ipv4options;
                0x0061: parse_u0_ipv4options;
                0x0062: parse_u0_ipv4options;
                0x0063: parse_u0_ipv4options;
                0x0064: parse_u0_ipv4options;
                0x0065: parse_u0_ipv4options;
                0x0066: parse_u0_ipv4options;
                0x0067: parse_u0_ipv4options;
                0x0068: parse_u0_ipv4options;
                0x0069: parse_u0_ipv4options;
                0x006A: parse_u0_ipv4options;
                0x006B: parse_u0_ipv4options;
                0x006C: parse_u0_ipv4options;
                0x006D: parse_u0_ipv4options;
                0x006E: parse_u0_ipv4options;
                0x006F: parse_u0_ipv4options;
                0x0070: parse_u0_ipv4options;
                0x0071: parse_u0_ipv4options;
                0x0072: parse_u0_ipv4options;
                0x0073: parse_u0_ipv4options;
                0x0074: parse_u0_ipv4options;
                0x0075: parse_u0_ipv4options;
                0x0076: parse_u0_ipv4options;
                0x0077: parse_u0_ipv4options;
                0x0078: parse_u0_ipv4options;
                0x0079: parse_u0_ipv4options;
                0x007A: parse_u0_ipv4options;
                0x007B: parse_u0_ipv4options;
                0x007C: parse_u0_ipv4options;
                0x007D: parse_u0_ipv4options;
                0x007E: parse_u0_ipv4options;
                0x007F: parse_u0_ipv4options;
                0x0080: parse_u0_ipv4options;
                0x0081: parse_u0_ipv4options;
                0x0082: parse_u0_ipv4options;
                0x0083: parse_u0_ipv4options;
                0x0084: parse_u0_ipv4options;
                0x0085: parse_u0_ipv4options;
                0x0086: parse_u0_ipv4options;
                0x0087: parse_u0_ipv4options;
                0x0088: parse_u0_ipv4options;
                0x0089: parse_u0_ipv4options;
                0x008A: parse_u0_ipv4options;
                0x008B: parse_u0_ipv4options;
                0x008C: parse_u0_ipv4options;
                0x008D: parse_u0_ipv4options;
                0x008E: parse_u0_ipv4options;
                0x008F: parse_u0_ipv4options;
                0x0090: parse_u0_ipv4options;
                0x0091: parse_u0_ipv4options;
                0x0092: parse_u0_ipv4options;
                0x0093: parse_u0_ipv4options;
                0x0094: parse_u0_ipv4options;
                0x0095: parse_u0_ipv4options;
                0x0096: parse_u0_ipv4options;
                0x0097: parse_u0_ipv4options;
                0x0098: parse_u0_ipv4options;
                0x0099: parse_u0_ipv4options;
                0x009A: parse_u0_ipv4options;
                0x009B: parse_u0_ipv4options;
                0x009C: parse_u0_ipv4options;
                0x009D: parse_u0_ipv4options;
                0x009E: parse_u0_ipv4options;
                0x009F: parse_u0_ipv4options;
                0x00A0: parse_u0_ipv4options;
                0x00A1: parse_u0_ipv4options;
                0x00A2: parse_u0_ipv4options;
                0x00A3: parse_u0_ipv4options;
                0x00A4: parse_u0_ipv4options;
                0x00A5: parse_u0_ipv4options;
                0x00A6: parse_u0_ipv4options;
                0x00A7: parse_u0_ipv4options;
                0x00A8: parse_u0_ipv4options;
                0x00A9: parse_u0_ipv4options;
                0x00AA: parse_u0_ipv4options;
                0x00AB: parse_u0_ipv4options;
                0x00AC: parse_u0_ipv4options;
                0x00AD: parse_u0_ipv4options;
                0x00AE: parse_u0_ipv4options;
                0x00AF: parse_u0_ipv4options;
                0x00B0: parse_u0_ipv4options;
                0x00B1: parse_u0_ipv4options;
                0x00B2: parse_u0_ipv4options;
                0x00B3: parse_u0_ipv4options;
                0x00B4: parse_u0_ipv4options;
                0x00B5: parse_u0_ipv4options;
                0x00B6: parse_u0_ipv4options;
                0x00B7: parse_u0_ipv4options;
                0x00B8: parse_u0_ipv4options;
                0x00B9: parse_u0_ipv4options;
                0x00BA: parse_u0_ipv4options;
                0x00BB: parse_u0_ipv4options;
                0x00BC: parse_u0_ipv4options;
                0x00BD: parse_u0_ipv4options;
                0x00BE: parse_u0_ipv4options;
                0x00BF: parse_u0_ipv4options;
                0x00C0: parse_u0_ipv4options;
                0x00C1: parse_u0_ipv4options;
                0x00C2: parse_u0_ipv4options;
                0x00C3: parse_u0_ipv4options;
                0x00C4: parse_u0_ipv4options;
                0x00C5: parse_u0_ipv4options;
                0x00C6: parse_u0_ipv4options;
                0x00C7: parse_u0_ipv4options;
                0x00C8: parse_u0_ipv4options;
                0x00C9: parse_u0_ipv4options;
                0x00CA: parse_u0_ipv4options;
                0x00CB: parse_u0_ipv4options;
                0x00CC: parse_u0_ipv4options;
                0x00CD: parse_u0_ipv4options;
                0x00CE: parse_u0_ipv4options;
                0x00CF: parse_u0_ipv4options;
                0x00D0: parse_u0_ipv4options;
                0x00D1: parse_u0_ipv4options;
                0x00D2: parse_u0_ipv4options;
                0x00D3: parse_u0_ipv4options;
                0x00D4: parse_u0_ipv4options;
                0x00D5: parse_u0_ipv4options;
                0x00D6: parse_u0_ipv4options;
                0x00D7: parse_u0_ipv4options;
                0x00D8: parse_u0_ipv4options;
                0x00D9: parse_u0_ipv4options;
                0x00DA: parse_u0_ipv4options;
                0x00DB: parse_u0_ipv4options;
                0x00DC: parse_u0_ipv4options;
                0x00DD: parse_u0_ipv4options;
                0x00DE: parse_u0_ipv4options;
                0x00DF: parse_u0_ipv4options;
                0x00E0: parse_u0_ipv4options;
                0x00E1: parse_u0_ipv4options;
                0x00E2: parse_u0_ipv4options;
                0x00E3: parse_u0_ipv4options;
                0x00E4: parse_u0_ipv4options;
                0x00E5: parse_u0_ipv4options;
                0x00E6: parse_u0_ipv4options;
                0x00E7: parse_u0_ipv4options;
                0x00E8: parse_u0_ipv4options;
                0x00E9: parse_u0_ipv4options;
                0x00EA: parse_u0_ipv4options;
                0x00EB: parse_u0_ipv4options;
                0x00EC: parse_u0_ipv4options;
                0x00ED: parse_u0_ipv4options;
                0x00EE: parse_u0_ipv4options;
                0x00EF: parse_u0_ipv4options;
                0x00F0: parse_u0_ipv4options;
                0x00F1: parse_u0_ipv4options;
                0x00F2: parse_u0_ipv4options;
                0x00F3: parse_u0_ipv4options;
                0x00F4: parse_u0_ipv4options;
                0x00F5: parse_u0_ipv4options;
                0x00F6: parse_u0_ipv4options;
                0x00F7: parse_u0_ipv4options;
                0x00F8: parse_u0_ipv4options;
                0x00F9: parse_u0_ipv4options;
                0x00FA: parse_u0_ipv4options;
                0x00FB: parse_u0_ipv4options;
                0x00FC: parse_u0_ipv4options;
                0x00FD: parse_u0_ipv4options;
                0x00FE: parse_u0_ipv4options;
                0x00FF: parse_u0_ipv4options;
                default: parse_u0_ipv4options;
        }
    }

    state parse_u0_ipv4options {
        b.extract(hdr.u0_ipv4options,
                    (bit<32>)(((bit<16>)hdr.u0_ipv4.ihl - 5) * 32));
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
    apply { b.emit(hdr.u0_ipv4); }
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
    apply { b.emit(hdr.u0_ipv4); }
}

Pipeline(ParserI(), IngressP(), DeparserI(), ParserE(), EgressP(), DeparserE()) pipe;
Switch(pipe) main;