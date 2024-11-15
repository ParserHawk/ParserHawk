#include <core.p4>
#include <v1model.p4>

// 112
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

//32
header int_switch_id_header_t {
    bit<1>  bos;
    bit<31> switch_id;
}

//32
header icmp_t {
    bit<16> typeCode;
    bit<16> hdrChecksum;
}

// 160
header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> srcAddr;
    bit<32> dstAddr;
}

// 320
header ipv6_t {
    bit<4>   version;
    bit<8>   trafficClass;
    bit<20>  flowLabel;
    bit<16>  payloadLen;
    bit<8>   nextHdr;
    bit<8>   hopLimit;
    bit<128> srcAddr;
    bit<128> dstAddr;
}

// 160
header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<4>  res;
    bit<8>  flags;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

// 64
header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

// 32
header int_value_t {
    bit<1>  bos;
    bit<31> val;
}

struct metadata {
    /* empty */
}

struct headers {
    int_switch_id_header_t                  int_switch_id_header;  // can be anything
    int_value_t                             int_val; // can be 1 + "anything" 31 time
    ethernet_t                              inner_ethernet;
    ipv4_t                                  inner_ipv4;
    ipv6_t                                  inner_ipv6;
    tcp_t                                   inner_tcp;
    udp_t                                   inner_udp;
    icmp_t                                  inner_icmp;
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

@name(".parse_all_int_meta_value_heders") state start {
        packet.extract(hdr.int_switch_id_header);
        transition parse_int_val;
    }

@name(".parse_int_val") state parse_int_val {
        packet.extract(hdr.int_val);
        transition select(hdr.int_val.bos) {
            1w1: parse_inner_ethernet;
            default: accept;
        }
    }

@name(".parse_inner_ethernet") state parse_inner_ethernet {
        packet.extract(hdr.inner_ethernet);
        transition select(hdr.inner_ethernet.etherType) {
            16w0x800: parse_inner_ipv4;
            16w0x86dd: parse_inner_ipv6;
            default: accept;
        }
    }

@name(".parse_inner_ipv4") state parse_inner_ipv4 {
        packet.extract(hdr.inner_ipv4);
        transition select(hdr.inner_ipv4.fragOffset, hdr.inner_ipv4.ihl, hdr.inner_ipv4.protocol) {
            (13w0x0, 4w0x5, 8w0x1): parse_inner_icmp;
            (13w0x0, 4w0x5, 8w0x6): parse_inner_tcp;
            (13w0x0, 4w0x5, 8w0x11): parse_inner_udp;
            default: accept;
        }
    }
    @name(".parse_inner_ipv6") state parse_inner_ipv6 {
        packet.extract(hdr.inner_ipv6);
        transition select(hdr.inner_ipv6.nextHdr) {
            8w58: parse_inner_icmp;
            8w6: parse_inner_tcp;
            8w17: parse_inner_udp;
            default: accept;
        }
    }

@name(".parse_inner_icmp") state parse_inner_icmp {
        packet.extract(hdr.inner_icmp);
        transition accept;
    }
@name(".parse_inner_tcp") state parse_inner_tcp {
        packet.extract(hdr.inner_tcp);
        transition accept;
    }
@name(".parse_inner_udp") state parse_inner_udp {
        packet.extract(hdr.inner_udp);
        transition accept;
    }

}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    apply {
    }
}


control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {  }
}

control MyDeparser(packet_out packet, in headers hdr) {
    apply { }
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;