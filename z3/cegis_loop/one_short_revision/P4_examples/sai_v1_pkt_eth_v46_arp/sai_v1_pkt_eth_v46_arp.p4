state parse_packet_out_header {
    packet.extract(headers.packet_out_header);  // 1-bit
    transition parse_ethernet;
  }

  state parse_ethernet {
    packet.extract(headers.ethernet);   // 16-bit
    transition select(headers.ethernet.ether_type) {
      ETHERTYPE_IPV4: parse_ipv4; // 0x0800
      ETHERTYPE_IPV6: parse_ipv6; // 0x86dd
      ETHERTYPE_ARP:  parse_arp;  // 0x0806
      _:              accept;
    }
  }

  state parse_ipv4 {  
    packet.extract(headers.ipv4); // 1-bit
    transition accept;
  }

  state parse_ipv6 {
    packet.extract(headers.ipv6);  // 1-bit
    transition accept;
  }

  state parse_arp {
    packet.extract(headers.arp);  // 1-bit
    transition accept;
  }