#include <core.p4>
#include <v1model.p4>

/**
2. If eth is 0, go to ipv4, if eth is 1 go to ipv6, otherwise just accept
3a. If ipv4 is 0, go to a               3b. If ipv6 is 0, go to b
4a. If a is 0, go to a                  4b, If b is 0, go to b
*/

header ethernet_t {
    bit<16>   etherType;
}

header ipv4_t {
    bit<8>    version;
}

header ipv6_t {
    bit<16>    version;
}

header a_t {
    bit<8>    val;
}

header b_t {
    bit<8>    wal;
}

struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ipv6_t       ipv6;
    a_t          a;
    b_t          b;
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType[7:0]) {
            0 : v4;
            1 : v6;
            default : accept;
        }
    }

    state v4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.version) {
            0: va;
            default : accept;
        }
    }

    state v6 {
        packet.extract(hdr.ipv6);
        transition select(hdr.ipv6.version) {
            0: vb;
            default : accept;
        }
    }

    state va {
        packet.extract(hdr.a);
        transition select(hdr.a.val) {
            0: va;
            default: accept;
        }
    }

    state vb {
        packet.extract(hdr.b);
        transition select(hdr.b.wal) {
            0: vb;
            default: accept;
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
