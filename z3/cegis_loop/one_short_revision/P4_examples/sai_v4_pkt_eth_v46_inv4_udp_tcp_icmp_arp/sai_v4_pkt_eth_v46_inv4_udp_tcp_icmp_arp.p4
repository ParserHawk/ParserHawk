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
    packet.extract(headers.ipv4); // 8-bit
    transition select(headers.ipv4.protocol) {
      IP_PROTOCOL_IPV4: parse_ipv4_in_ip;
      IP_PROTOCOL_UDP:  parse_udp;  // 0x11
      IP_PROTOCOL_TCP:  parse_tcp;  // 0x06
      IP_PROTOCOL_ICMP: parse_icmp; // 0x01
      _:                accept;
    }
    transition accept;
  }

  state parse_ipv6 {
    packet.extract(headers.ipv6);  // 8-bit
    transition select(headers.ipv6.next_header) {
      IP_PROTOCOL_ICMPV6: parse_icmp;  // 0x3a
      IP_PROTOCOL_TCP:    parse_tcp; // 0x06
      IP_PROTOCOL_UDP:    parse_udp; // 0x11
      _:                  accept;
    }
    transition accept;
  }

  state parse_ipv4_in_ip {
    packet.extract(headers.inner_ipv4);  // 8-bit
    transition select(headers.inner_ipv4.protocol) {
      IP_PROTOCOL_UDP:  parse_udp;
      IP_PROTOCOL_ICMP: parse_icmp; 
      IP_PROTOCOL_TCP:  parse_tcp;
      _:                accept;
    }
  }

  state parse_tcp {
    packet.extract(headers.tcp);  // 1-bit
    transition accept;
  }

  state parse_udp {
    packet.extract(headers.udp);  // 1-bit
    transition accept;
  }

  state parse_icmp {
    packet.extract(headers.icmp); // 1-bit
    transition accept;
  }

  state parse_arp {
    packet.extract(headers.arp);  // 1-bit
    transition accept;
  }