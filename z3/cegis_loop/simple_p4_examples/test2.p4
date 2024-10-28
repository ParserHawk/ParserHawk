#include <core.p4>
#include <v1model.p4>

/**
2. If eth is 0, go to ipv4, if eth is 1 go to ipv6, otherwise just accept
3a. If ipv4 is 0, go to a               3b. If ipv6 is 0, go to b
4a. If a is 0, go to a                  4b, If b is 0, go to b
*/

header ethernet_t {
    bit<16>   etherType1;
    bit<16>   etherType2;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType1, hdr.ethernet.etherType2) {
            (0, 1) : start;
            default : accept;
        }
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
