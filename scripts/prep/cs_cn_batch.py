"""Prep guides: Computer networks (CS fundamentals track)."""

GUIDES = [
    dict(
        id='guide-cs-fundamentals-cn-osi-tcpip-layers', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='OSI and TCP/IP layers', order=1,
        summary="How network communication is split into layers, what each layer is responsible for, and how the OSI and TCP/IP models line up.",
        sections=[
            dict(title='Why networks are built in layers', text=(
                "Sending a web page from a server to your laptop involves many separate problems: turning bits into signals on a wire, "
                "getting a frame across one link, finding a path across many networks, making sure no data is lost, and agreeing on what the bytes mean. "
                "Layering splits these problems apart. Each layer offers a service to the layer above it and relies only on the layer below, so you can swap "
                "Wi-Fi for Ethernet without touching your browser.\n\n"
                "On the way down the stack, each layer wraps the data it receives in its own header. This is called encapsulation. On the way up at the receiver, "
                "each layer reads and strips its own header and hands the rest upward. The unit of data has a different name at each level: a segment at the transport "
                "layer (a datagram for UDP), a packet at the network layer, a frame at the data link layer, and raw bits at the physical layer. "
                "Interviewers like to check that you know these names and which layer adds which address."
            )),
            dict(title='The seven OSI layers', text=(
                "The OSI model lists seven layers. Counting from the bottom: the physical layer moves raw bits over a medium, covering cables, connectors, voltages "
                "and radio signals; hubs and repeaters work here. The data link layer moves frames between two directly connected devices, using MAC addresses and "
                "a checksum to catch corrupted frames; Ethernet, Wi-Fi and switches live here. The network layer gives every host a logical address and routes packets "
                "across many networks; IP and ICMP are the examples, and routers are the devices.\n\n"
                "The transport layer delivers data between processes on two hosts, using port numbers; TCP and UDP are here. The session layer sets up, manages and "
                "ends conversations between applications. The presentation layer deals with how data is represented, such as character encoding, compression and "
                "encryption. The application layer holds the protocols programs use directly, such as HTTP, DNS, SMTP and FTP. "
                "A common memory aid from the bottom is Please Do Not Throw Sausage Pizza Away."
            )),
            dict(title='How the TCP/IP model maps onto OSI', text=(
                "OSI is a reference vocabulary. The protocols the internet actually runs on follow the simpler TCP/IP model, which has four layers. The link layer "
                "(sometimes called network access) covers what OSI splits into physical and data link. The internet layer matches the OSI network layer and is where IP sits. "
                "The transport layer is the same idea in both models. The application layer of TCP/IP absorbs OSI session, presentation and application, because "
                "real protocols such as HTTP handle those concerns themselves.\n\n"
                "Some textbooks teach a five-layer hybrid that keeps physical and data link separate but otherwise follows TCP/IP. If an interviewer asks how many "
                "layers TCP/IP has, say four and mention the five-layer variant. Also be ready for the honest answer that some protocols do not fit neatly: TLS, for "
                "example, sits between TCP and HTTP and is often described as presentation-layer work even though it is not a separate TCP/IP layer."
            )),
            dict(title='Following one request down and across the stack', text=(
                "Say your browser requests a page from a server over plain HTTP. The application layer builds the GET request. TCP adds a header with a source port "
                "the operating system picked, such as 52000, and destination port 80. IP adds your laptop's address as the source and the server's address as the "
                "destination. Ethernet then adds a frame header whose destination MAC is your default gateway, the first router, not the far-away server.\n\n"
                "That router removes the frame, reads the destination IP, looks it up in its routing table and wraps the same packet in a new frame addressed to "
                "the next hop. This repeats at every router. So, ignoring NAT, the IP addresses stay the same end to end, while the MAC addresses change on every link. "
                "A hub just repeats bits, a switch reads MAC addresses to forward frames inside one network, and a router reads IP addresses to move packets between networks."
            )),
        ],
        keyPoints=[
            "Each layer serves the one above and adds its own header on the way down (encapsulation).",
            "Data units: segment at transport, packet at network, frame at data link, bits at physical.",
            "OSI has seven layers; TCP/IP has four: link, internet, transport, application.",
            "Switches forward by MAC address (layer 2); routers forward by IP address (layer 3).",
            "Across a path without NAT, IP addresses stay the same while MAC addresses are rewritten at every hop.",
        ],
        challenges=[
            dict(id='challenge-cn-osi-tcpip-layers-q1', kind='prediction', title='What a switch reads',
                 prompt="A frame arrives at a switch inside an office LAN. Which field does the switch use to decide which port to send it out of?",
                 options=["The destination IP address", "The destination MAC address", "The destination TCP port", "The domain name in the request"],
                 answer=1,
                 explanation="A switch is a data link (layer 2) device, so it forwards frames by looking up the destination MAC address in its MAC table. IP addresses are read by routers at layer 3, ports are a transport-layer idea the switch ignores, and domain names are resolved by DNS long before the frame exists.",
                 hint="Think about which layer a switch works at and what addresses exist at that layer."),
            dict(id='challenge-cn-osi-tcpip-layers-q2', kind='prediction', title='What changes at each hop',
                 prompt="A packet travels from your laptop to a server through three routers, with no NAT on the path. Which values are rewritten on every hop?",
                 options=["The destination IP address", "The TCP destination port", "The source and destination MAC addresses", "Nothing; every header stays the same"],
                 answer=2,
                 explanation="Each router strips the incoming frame and builds a new one for the next link, so the source and destination MAC addresses change on every hop. The IP addresses identify the two end hosts and stay the same without NAT, and the TCP port is untouched because routers do not work at the transport layer.",
                 hint="MAC addresses only mean something on a single link."),
            dict(id='challenge-cn-osi-tcpip-layers-q3', kind='prediction', title='Delivering to the right program',
                 prompt="A server runs a web server and an SSH server on the same IP address. Which layer makes sure an incoming segment reaches the right one of these programs?",
                 options=["Transport layer, using port numbers", "Network layer, using IP addresses", "Session layer, using session IDs", "Data link layer, using MAC addresses"],
                 answer=0,
                 explanation="Both programs share one IP address, so the network layer only gets the data to the right machine. The transport layer then uses the destination port (for example 80 or 22) to hand the data to the right process. MAC addresses only get frames across one link, and the session layer does not do this demultiplexing.",
                 hint="The IP address is the same for both programs, so something finer is needed."),
            dict(id='challenge-cn-osi-tcpip-layers-q4', kind='prediction', title='Mapping the models',
                 prompt="Which OSI layers are covered by the single application layer of the TCP/IP model?",
                 options=["Only the OSI application layer", "OSI transport, session, presentation and application", "OSI data link and physical", "OSI session, presentation and application"],
                 answer=3,
                 explanation="TCP/IP folds OSI layers 5, 6 and 7 (session, presentation and application) into one application layer, because real protocols handle those concerns themselves. Transport is its own layer in both models, and data link plus physical map to the TCP/IP link layer instead.",
                 hint="Transport exists as its own layer in both models."),
            dict(id='challenge-cn-osi-tcpip-layers-q5', kind='prediction', title='What a router does with a frame',
                 prompt="A router receives a frame on one interface. What does it do to move the data toward its destination?",
                 options=["Forwards the frame unchanged out of the port matching its destination MAC",
                          "Removes the frame header, looks up the destination IP in its routing table, and puts the packet in a new frame for the next hop",
                          "Reads the TCP destination port and picks the interface assigned to that port"],
                 answer=1,
                 explanation="A router is a layer 3 device: it de-encapsulates the frame, makes its decision from the destination IP address, and re-encapsulates the packet for the next link. Forwarding frames unchanged by MAC is what a switch does, and routers do not choose interfaces by transport port.",
                 hint="The destination MAC on an incoming frame is the router's own address."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-cn-ip-subnetting', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='IP addressing and subnetting', order=2,
        summary="How IPv4 addresses split into network and host parts, and how to work out subnet sizes, network addresses and broadcast addresses by hand.",
        sections=[
            dict(title='What an IPv4 address is', text=(
                "An IPv4 address is a 32-bit number, written as four 8-bit octets in decimal, such as 192.168.10.77. Every address is split into a network part, "
                "which identifies the subnet, and a host part, which identifies one machine on it. The prefix length after the slash says how many leading bits "
                "belong to the network. In 192.168.10.77/24, the first 24 bits are the network, so the mask is 255.255.255.0.\n\n"
                "The old class system (A, B and C with fixed /8, /16 and /24 boundaries) wasted huge numbers of addresses, so it was replaced by CIDR, which "
                "allows any prefix length. Three ranges are reserved for private networks and are not routed on the public internet: 10.0.0.0/8, 172.16.0.0/12 "
                "and 192.168.0.0/16. Your home router uses NAT to let many private addresses share one public address. 127.0.0.0/8 is reserved for loopback. "
                "IPv6 solves the shortage with 128-bit addresses, and a normal LAN gets a /64."
            )),
            dict(title='Counting addresses in a block', text=(
                "If the prefix is /n, there are 32 minus n host bits, and the block holds 2 to the power of that number addresses. Two of them are not given to hosts: "
                "the address with all host bits set to 0 is the network address, and the one with all host bits set to 1 is the broadcast address. So usable hosts "
                "equal 2 to the power of the host bits, minus 2.\n\n"
                "A /24 has 8 host bits: 256 addresses, 254 usable. A /28 has 4 host bits: 16 addresses, 14 usable. A /30 has 2 host bits: 4 addresses, 2 usable, "
                "which is why /30 was the classic choice for a link between two routers. A /32 names a single host.\n\n"
                "A handy shortcut is the block size. Look at the octet where the mask stops being 255, and subtract that mask value from 256. For a /26 the last "
                "octet of the mask is 192, so the block size is 64, and subnets start at multiples of 64 in that octet."
            )),
            dict(title='Worked example: a /26', text=(
                "Take the host 192.168.10.77/26. A /26 means 24 bits for the first three octets plus 2 more bits in the fourth. Those two bits are worth 128 and 64, "
                "so the mask is 255.255.255.192. The block size is 256 minus 192, which is 64, so the subnets in the last octet start at 0, 64, 128 and 192.\n\n"
                "77 lies between 64 and 127, so the network address is 192.168.10.64 and the broadcast address is 192.168.10.127, one less than the next block. "
                "Usable hosts run from 192.168.10.65 to 192.168.10.126, which is 62 addresses, matching 2 to the power of 6 minus 2.\n\n"
                "You can check it in binary. 77 is 01001101. The mask octet 192 is 11000000. ANDing them keeps only the top two bits, giving 01000000, which is 64. "
                "Setting the six host bits to 1 instead gives 01111111, which is 127. Both methods agree, and in an interview it is worth saying both out loud."
            )),
            dict(title='Splitting a network to fit a design', text=(
                "Subnetting usually starts from a requirement. Suppose you own 192.168.10.0/24 and need four equal subnets. Four subnets need 2 extra network bits, "
                "because 2 to the power of 2 is 4, so each becomes a /26: 192.168.10.0, .64, .128 and .192, each with 62 usable hosts.\n\n"
                "Now suppose one department needs 100 hosts. You need the smallest number of host bits h with 2 to the power of h minus 2 at least 100. Six bits gives "
                "62, too few; seven gives 126, enough. Seven host bits means a /25.\n\n"
                "When departments need different sizes, use variable length subnet masks and hand out the largest blocks first, so smaller blocks fill the gaps "
                "cleanly without overlapping. To test whether two hosts are on the same subnet, compute each one's network address with its own mask and compare."
            )),
        ],
        keyPoints=[
            "IPv4 is 32 bits; the /n prefix gives the network bits and 32 minus n gives the host bits.",
            "Usable hosts = 2^(host bits) - 2 for a /30 or shorter, because the network and broadcast addresses are reserved.",
            "Block size = 256 minus the mask value in the octet where the mask stops being 255.",
            "192.168.10.77/26 sits in 192.168.10.64 to 192.168.10.127, with 62 usable hosts.",
            "Private ranges are 10.0.0.0/8, 172.16.0.0/12 and 192.168.0.0/16.",
        ],
        challenges=[
            dict(id='challenge-cn-ip-subnetting-q1', kind='prediction', title='Network address of a /27',
                 prompt="What is the network address of the host 10.1.5.200/27?",
                 options=["10.1.5.192", "10.1.5.160", "10.1.5.200", "10.1.5.224"],
                 answer=0,
                 explanation="A /27 leaves 5 host bits, so the mask's last octet is 224 and the block size is 256 - 224 = 32. Blocks start at 0, 32, 64, 96, 128, 160, 192, 224. 200 falls in the block 192 to 223, so the network is 10.1.5.192. 160 is the previous block, 224 is the next one, and 200 is the host itself, not its network.",
                 hint="Find the block size, then the largest multiple of it that is not above 200."),
            dict(id='challenge-cn-ip-subnetting-q2', kind='prediction', title='Hosts in a /28',
                 prompt="How many hosts can you assign addresses to in a /28 subnet?",
                 options=["16", "30", "14"],
                 answer=2,
                 explanation="A /28 has 32 - 28 = 4 host bits, so it holds 2^4 = 16 addresses. The all-zeros address is the network address and the all-ones address is the broadcast, leaving 14 usable. 16 forgets the two reserved addresses, and 30 is the usable count for a /27.",
                 hint="Count the host bits, then remember two addresses are reserved."),
            dict(id='challenge-cn-ip-subnetting-q3', kind='prediction', title='Smallest subnet for 50 hosts',
                 prompt="A lab needs 50 host addresses. What is the longest prefix (smallest subnet) that fits?",
                 options=["/27", "/25", "/24", "/26"],
                 answer=3,
                 explanation="You need 2^h - 2 to be at least 50. With h = 5 you get 30, too few. With h = 6 you get 62, enough, so the prefix is 32 - 6 = /26. A /27 is too small, and /25 or /24 would work but waste addresses.",
                 hint="Try host-bit counts upward until 2^h - 2 reaches 50."),
            dict(id='challenge-cn-ip-subnetting-q4', kind='prediction', title='Broadcast of a /22',
                 prompt="What is the broadcast address of the network 172.16.40.0/22?",
                 options=["172.16.40.255", "172.16.43.255", "172.16.44.255", "172.16.47.255"],
                 answer=1,
                 explanation="A /22 ends 2 bits into the third octet, so the mask is 255.255.252.0 and the block size in the third octet is 256 - 252 = 4. The network spans third-octet values 40, 41, 42 and 43, so the last address is 172.16.43.255. 172.16.40.255 is only the end of the first /24 inside it, 44 is the start of the next block, and 47 would need a block size of 8.",
                 hint="The interesting octet here is the third one, not the fourth."),
            dict(id='challenge-cn-ip-subnetting-q5', kind='prediction', title='Same subnet or not',
                 prompt="Two hosts are configured as 192.168.1.100/25 and 192.168.1.130/25. Are they on the same subnet?",
                 options=["No: .100 is in 192.168.1.0/25 and .130 is in 192.168.1.128/25",
                          "Yes, because both addresses start with 192.168.1",
                          "Yes, because a /25 holds 126 hosts and both fit"],
                 answer=0,
                 explanation="A /25 has block size 128, so 192.168.1.0/24 splits into 0 to 127 and 128 to 255. 100 lands in the first and 130 in the second, so their network addresses differ and traffic between them must go through a router. Sharing the first three octets only matters for a /24, and the host count of a subnet says nothing about which block each address is in.",
                 hint="Compute each host's network address with the /25 mask."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-cn-tcp-vs-udp', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='TCP vs UDP', order=3,
        summary="What the two main transport protocols guarantee, how TCP sets up connections and controls its sending rate, and when to choose each.",
        sections=[
            dict(title='What the transport layer adds', text=(
                "IP gets a packet to the right machine, but a machine runs many programs. The transport layer adds port numbers so data reaches the right process. "
                "A socket is an IP address plus a port, and a TCP connection is identified by four values: source IP, source port, destination IP and destination port. "
                "That is how one web server on port 443 can talk to thousands of clients at once; each client connection has a different source address or port.\n\n"
                "Some well-known ports come up often: 80 for HTTP, 443 for HTTPS, 53 for DNS, 22 for SSH and 25 for SMTP. Both TCP and UDP provide ports and a "
                "checksum to detect corruption. Everything else on top of that, such as reliability, ordering and rate control, is what separates them, and "
                "interviewers want you to explain the trade-off rather than just list features."
            )),
            dict(title='TCP: a reliable, ordered byte stream', text=(
                "TCP is connection-oriented. Before data flows, the two sides do a three-way handshake. The client sends SYN with an initial sequence number, say 1000. "
                "The server replies with SYN-ACK, carrying its own initial sequence number, say 5000, and an acknowledgement of 1001. The client then sends ACK 5001. "
                "Each side now knows the other is reachable and where its byte numbering starts. A SYN consumes one sequence number, which is why the acknowledgements are one higher.\n\n"
                "Sequence numbers count bytes. The receiver acknowledges the next byte it expects, and the sender keeps unacknowledged data so it can resend it. "
                "A segment is retransmitted when a timer runs out, or earlier when three duplicate acknowledgements suggest it was lost (fast retransmit). "
                "The receiver reorders and drops duplicates, so the application sees an exact copy of the stream. Closing uses FIN and ACK in each direction, "
                "so a normal close takes four segments, though the middle two can be combined."
            )),
            dict(title='Flow control versus congestion control', text=(
                "These two are easy to mix up, so separate them by who is being protected. Flow control protects the receiver. In every segment the receiver advertises "
                "a window, the free space in its buffer. The sender may not have more unacknowledged bytes in flight than that. If the window drops to zero, the sender "
                "stops sending new data and periodically sends a small probe until the window opens again.\n\n"
                "Congestion control protects the network. The sender keeps its own congestion window, which it grows while things go well and shrinks when loss "
                "suggests the path is overloaded. In slow start the window roughly doubles every round-trip time until it reaches a threshold; after that, in congestion "
                "avoidance, it grows by about one segment per round trip. On loss it cuts back sharply. This pattern is called additive increase, multiplicative decrease.\n\n"
                "The amount the sender can actually have in flight is the smaller of the two windows."
            )),
            dict(title='UDP and how to choose', text=(
                "UDP is connectionless and minimal. Its header is 8 bytes: source port, destination port, length and checksum. There is no handshake, no acknowledgement, "
                "no retransmission, no ordering and no congestion control. Each datagram stands alone and may be lost, duplicated or arrive out of order.\n\n"
                "That sounds like a weakness, but it suits some jobs. A DNS lookup is one small question and one small answer, so a handshake would double the delay; "
                "if the reply is lost, the client simply asks again. Voice and video calls and online games care more about fresh data than complete data: a retransmitted "
                "audio sample that arrives late is useless. DHCP also uses UDP, because a new host has no address yet to hold a connection with.\n\n"
                "Choose TCP when every byte must arrive correctly and in order: web pages, file transfers, email and SSH. Note that QUIC, which carries HTTP/3, runs "
                "over UDP and builds its own reliability and congestion control on top, mainly to set up connections faster and avoid one lost packet stalling every stream."
            )),
        ],
        keyPoints=[
            "Both TCP and UDP use ports and checksums; only TCP adds reliability, ordering and rate control.",
            "Three-way handshake: SYN (seq x), SYN-ACK (seq y, ack x+1), ACK (ack y+1).",
            "Flow control protects the receiver via the advertised window; congestion control protects the network via the congestion window.",
            "A TCP sender can have at most min(receiver window, congestion window) bytes in flight.",
            "UDP suits short request-response and real-time traffic where late data is worthless.",
        ],
        challenges=[
            dict(id='challenge-cn-tcp-vs-udp-q1', kind='prediction', title='Handshake numbers',
                 prompt="A client sends SYN with sequence number 1000. The server answers with SYN-ACK, sequence number 5000. What acknowledgement number does the client put in its final ACK?",
                 options=["1001", "5000", "5001", "6000"],
                 answer=2,
                 explanation="The ACK number is the next byte the client expects from the server. The server's SYN used sequence number 5000 and a SYN consumes one number, so the client acknowledges 5001. 1001 is what the server acknowledged to the client, 5000 forgets that SYN counts, and 6000 adds an unrelated offset.",
                 hint="An acknowledgement names the next sequence number expected, and a SYN uses one up."),
            dict(id='challenge-cn-tcp-vs-udp-q2', kind='prediction', title='A zero window',
                 prompt="Mid-transfer, the receiver advertises a window of 0. What does the TCP sender do?",
                 options=["Stops sending new data and periodically probes until the window reopens",
                          "Halves its congestion window because the network is congested",
                          "Resets the connection because the receiver has failed"],
                 answer=0,
                 explanation="A zero window is flow control: the receiver's buffer is full. The sender pauses and sends small window probes so it learns when space frees up. It is not a sign of network congestion, so the congestion window is not the mechanism here, and the connection is healthy, so it is not reset.",
                 hint="Ask whether the receiver or the network is the one that is overloaded."),
            dict(id='challenge-cn-tcp-vs-udp-q3', kind='prediction', title='Why a call app uses UDP',
                 prompt="A video-calling app sends its audio over UDP rather than TCP. What is the best reason?",
                 options=["UDP encrypts audio automatically",
                          "Retransmitted audio would arrive too late to play, so dropping a lost packet is better than waiting for it",
                          "UDP guarantees in-order delivery with less overhead than TCP",
                          "UDP headers are larger, leaving room for timing data"],
                 answer=1,
                 explanation="Real-time audio is only useful if it arrives on time. TCP would stall the stream to recover a lost segment, which causes freezes; UDP lets the app skip the gap and keep going. UDP does not encrypt anything, does not guarantee order, and its 8-byte header is smaller than TCP's 20-byte minimum.",
                 hint="Think about what a late sound sample is worth."),
            dict(id='challenge-cn-tcp-vs-udp-q4', kind='prediction', title='How much can be in flight',
                 prompt="A TCP sender's congestion window is 40 KB and the receiver's advertised window is 16 KB. How much unacknowledged data can the sender have in flight?",
                 options=["40 KB", "56 KB", "24 KB", "16 KB"],
                 answer=3,
                 explanation="The sender must respect both limits, so it uses the smaller one: min(40, 16) = 16 KB. 40 KB would overflow the receiver's buffer, 56 KB adds the windows together, and 24 KB is their difference, which has no meaning here.",
                 hint="Two separate limits apply at the same time."),
            dict(id='challenge-cn-tcp-vs-udp-q5', kind='prediction', title='Slow start growth',
                 prompt="A TCP connection starts slow start with a congestion window of 1 segment. Assuming no loss and a threshold far above these values, what is the window after 3 round-trip times?",
                 options=["4 segments", "8 segments", "3 segments", "16 segments"],
                 answer=1,
                 explanation="In slow start the window doubles every round trip: 1, then 2 after one RTT, 4 after two, and 8 after three. 4 stops one round trip early, 3 assumes linear growth (that is congestion avoidance), and 16 is one doubling too many.",
                 hint="Slow start grows exponentially, not linearly."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-cn-routing-basics', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='Routing basics', order=4,
        summary="How routers pick the next hop with longest prefix match, and how distance-vector and link-state protocols build routing tables.",
        sections=[
            dict(title='What a router decides', text=(
                "A router moves packets between networks. For each packet it looks up the destination IP address in its routing table. Each entry holds a prefix, "
                "a next hop, an outgoing interface and a metric. Several entries can match, and the rule is longest prefix match: the most specific entry wins.\n\n"
                "Suppose the table has 10.0.0.0/8 via router A, 10.1.0.0/16 via router B and a default route 0.0.0.0/0 via router C. A packet for 10.1.4.9 matches "
                "all three, and the /16 is longest, so it goes to B. A packet for 10.2.0.1 matches the /8 and the default, so it goes to A. A packet for 8.8.8.8 only "
                "matches the default, so it goes to C.\n\n"
                "Each router also decrements the packet's TTL field. When TTL reaches 0, the router drops the packet and sends an ICMP Time Exceeded message back to the "
                "source. This stops packets looping forever, and traceroute uses it by sending packets with TTL 1, 2, 3 and so on to reveal each hop."
            )),
            dict(title='Static routes and dynamic routing', text=(
                "A static route is typed in by an administrator. It is simple, predictable and costs no bandwidth, but it does not react when a link fails. "
                "Static routes work well for small networks or for a single default route out to an internet provider.\n\n"
                "Dynamic routing protocols let routers tell each other what they can reach and recompute paths when something changes. Inside one organisation's "
                "network, an autonomous system, you find interior protocols such as RIP and OSPF. Between autonomous systems, the internet runs BGP.\n\n"
                "It helps to separate two jobs. Routing is the slower background work of building the table, sometimes called the control plane. Forwarding is the "
                "fast per-packet lookup that uses the table, called the data plane. Interview questions about RIP and OSPF are about routing; longest prefix match "
                "is about forwarding."
            )),
            dict(title='Distance-vector routing', text=(
                "In distance-vector routing, each router knows only its distance to every destination and which neighbour to use. Periodically it sends this list, "
                "its vector, to its neighbours. Each router then applies the Bellman-Ford rule: my cost to a destination is the minimum, over all neighbours, of the "
                "link cost to that neighbour plus the neighbour's advertised cost. If A reaches B at cost 2 and B advertises cost 7 to D, the path via B costs 9.\n\n"
                "RIP is the classic example. Its metric is hop count, 16 means unreachable, so paths are limited to 15 hops, and it sends updates every 30 seconds.\n\n"
                "The known weakness is count to infinity. When a link fails, two routers can keep learning the dead route from each other, each time adding one, "
                "slowly climbing toward the maximum. Fixes include split horizon (never advertise a route back to the neighbour you learned it from), poison reverse "
                "(advertise it back as unreachable), hold-down timers and the small maximum metric itself."
            )),
            dict(title='Link-state routing', text=(
                "In link-state routing, each router describes only its own directly connected links and their costs, and floods that description to every router "
                "in the area. Every router ends up with the same complete map of the network and runs Dijkstra's shortest path algorithm on it independently.\n\n"
                "OSPF is the standard example. Its cost is usually based on link bandwidth, and large networks are split into areas joined by a backbone area, area 0, "
                "so floods stay local. Because every router sees the whole map and recomputes as soon as a change arrives, link-state protocols converge faster and "
                "do not suffer count to infinity. The price is more memory and CPU.\n\n"
                "A short way to remember the difference: distance-vector routers tell their neighbours about the whole network, while link-state routers tell the whole "
                "network about their neighbours. BGP is a third style, path-vector: it advertises the full list of autonomous systems a route passes through, "
                "which prevents loops and lets operators apply business policy."
            )),
        ],
        keyPoints=[
            "Routers forward using longest prefix match; the default route 0.0.0.0/0 matches everything.",
            "TTL drops by one per hop; at 0 the packet is discarded and ICMP Time Exceeded is returned.",
            "Distance-vector (RIP) shares vectors with neighbours and uses Bellman-Ford; it can count to infinity.",
            "Link-state (OSPF) floods link information and runs Dijkstra on a full map; it converges faster.",
            "Interior protocols run inside an autonomous system; BGP connects autonomous systems.",
        ],
        challenges=[
            dict(id='challenge-cn-routing-basics-q1', kind='prediction', title='Longest prefix match',
                 prompt="A routing table has 172.16.0.0/16 via R1, 172.16.8.0/21 via R2 and 0.0.0.0/0 via R3. Where does a packet for 172.16.12.5 go?",
                 options=["R1", "R2", "R3", "It is dropped"],
                 answer=1,
                 explanation="A /21 has block size 8 in the third octet, so 172.16.8.0/21 covers 172.16.8.0 to 172.16.15.255, which includes 172.16.12.5. The /16 and the default also match, but /21 is the longest prefix, so R2 wins. R1 and R3 are less specific, and the packet is not dropped because at least one route matches.",
                 hint="Work out the range covered by the /21 first."),
            dict(id='challenge-cn-routing-basics-q2', kind='prediction', title='Distance-vector update',
                 prompt="Router A has two neighbours: B with link cost 2 and C with link cost 5. B advertises a cost of 7 to network D, and C advertises a cost of 3 to D. What does A record for D?",
                 options=["Cost 9, via B", "Cost 3, via C", "Cost 10, via both", "Cost 8, via C"],
                 answer=3,
                 explanation="Bellman-Ford adds each link cost to that neighbour's advertised cost: via B is 2 + 7 = 9 and via C is 5 + 3 = 8, so A picks C at cost 8. Cost 9 is the worse path, cost 3 ignores the link from A to C, and routes are not combined across neighbours.",
                 hint="Add the link cost to what each neighbour advertises, then take the smaller."),
            dict(id='challenge-cn-routing-basics-q3', kind='prediction', title='A cost that keeps climbing',
                 prompt="After a link fails, two neighbouring routers keep advertising a route to the lost network to each other, each raising the cost by one every round. What is this, and which kind of protocol suffers from it?",
                 options=["LSA flooding storm, in link-state protocols",
                          "Count to infinity, in distance-vector protocols",
                          "Route flapping, only in BGP"],
                 answer=1,
                 explanation="Distance-vector routers only know what neighbours tell them, so after a failure they can learn a stale route back from each other and keep adding one until they hit the maximum. Link-state routers each hold the full map and simply recompute, so they do not loop like this. Route flapping is a route going up and down repeatedly, which is a different problem.",
                 hint="Which design relies on second-hand distance reports?"),
            dict(id='challenge-cn-routing-basics-q4', kind='prediction', title='Why OSPF converges faster',
                 prompt="Why does OSPF usually react to a link failure faster than RIP?",
                 options=["Every OSPF router holds the full topology and reruns Dijkstra as soon as a link-state update arrives",
                          "OSPF uses hop count, which is quicker to calculate than bandwidth",
                          "OSPF sends its whole routing table to neighbours every 30 seconds"],
                 answer=0,
                 explanation="Once a link-state update is flooded, every OSPF router has the new map and recomputes its own shortest paths right away. RIP must wait for changes to spread neighbour by neighbour through periodic vectors. Hop count and 30-second full-table updates describe RIP, not OSPF.",
                 hint="Compare having the whole map with hearing summaries from neighbours."),
            dict(id='challenge-cn-routing-basics-q5', kind='prediction', title='Running out of TTL',
                 prompt="A packet leaves your laptop with TTL 3. The path to the server crosses 5 routers. What happens?",
                 options=["The server receives it with TTL 0",
                          "The first router drops it because 3 is less than 5",
                          "The third router reduces TTL to 0, drops it and sends ICMP Time Exceeded back to your laptop",
                          "It loops between routers until another route is found"],
                 answer=2,
                 explanation="Each router subtracts one: 3 becomes 2 at the first router, 1 at the second and 0 at the third, which then discards the packet and reports back with ICMP Time Exceeded. Routers do not check TTL against path length in advance, a packet is never delivered with TTL 0 here, and TTL is exactly the mechanism that prevents endless loops.",
                 hint="Subtract one at each router and see where it hits zero."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-cn-dns-http', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='DNS and HTTP', order=5,
        summary="How a name becomes an IP address, how HTTP requests and responses work, and what HTTPS adds on top.",
        sections=[
            dict(title='How DNS resolves a name', text=(
                "DNS is a distributed, hierarchical database that maps names to records such as IP addresses. When you type www.example.com, your machine first checks "
                "its own caches and hosts file. If there is no answer, the operating system's stub resolver sends the question to a recursive resolver, usually run by "
                "your network or a public provider.\n\n"
                "If the resolver has nothing cached, it walks the hierarchy. It asks a root server, which does not know the answer but refers it to the servers for .com. "
                "It asks a .com server, which refers it to the authoritative name servers for example.com. It asks one of those, which returns the actual record. "
                "The resolver caches the answer for as long as the record's TTL allows and returns it to you.\n\n"
                "Your machine's request is recursive: it expects a final answer. The resolver's requests are iterative: each server either answers or points somewhere else. "
                "DNS normally uses UDP port 53 and falls back to TCP for large responses and zone transfers."
            )),
            dict(title='Record types worth knowing', text=(
                "An A record maps a name to an IPv4 address, and an AAAA record maps it to an IPv6 address. A CNAME makes one name an alias for another; for example, "
                "www.shop.example could be a CNAME for shop.example, which in turn has an A record such as 203.0.113.10. MX records name the mail servers for a domain, "
                "each with a priority where lower numbers are tried first. NS records list the authoritative name servers for a zone. TXT records hold free text and are "
                "used for domain ownership checks and email anti-spoofing policies. PTR records support reverse lookups, from address back to name.\n\n"
                "Every record carries a TTL in seconds. A long TTL means fewer lookups and faster browsing, but a change you make will take longer to reach everyone, "
                "because resolvers keep serving the cached copy until it expires. Before a planned move, teams often lower the TTL a day ahead."
            )),
            dict(title='HTTP requests and methods', text=(
                "HTTP is a request-response protocol. A request has a method, a path, a version, headers and an optional body. A response has a status line, headers "
                "and usually a body. HTTP itself is stateless: the server does not remember earlier requests, so cookies or tokens in headers carry login state.\n\n"
                "GET reads a resource and should not change anything. POST submits data, often creating something new. PUT replaces a resource at a known path, PATCH "
                "changes part of it, and DELETE removes it. Two properties matter in interviews. A safe method, like GET or HEAD, does not change server state. An "
                "idempotent method gives the same end result whether you send it once or several times; GET, PUT and DELETE are idempotent, POST is not. That is why "
                "a client can safely retry a PUT after a timeout but must be careful retrying a POST.\n\n"
                "HTTP/1.1 reuses TCP connections, HTTP/2 multiplexes many requests over one connection, and HTTP/3 runs over QUIC."
            )),
            dict(title='Status codes and HTTPS', text=(
                "Status codes are grouped by first digit. 1xx is informational. 2xx is success: 200 OK, 201 Created, 204 No Content. 3xx is redirection: 301 for a "
                "permanent move, 302 for a temporary one, 304 Not Modified when the cached copy is still good. 4xx means the client did something wrong: 400 Bad Request, "
                "401 when you are not authenticated, 403 when the server refuses the request, typically because you are authenticated but not allowed, 404 Not Found, 429 Too Many Requests. 5xx means the server failed: "
                "500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable.\n\n"
                "HTTPS is HTTP sent over TLS, normally on port 443. During the TLS handshake the server presents a certificate signed by a certificate authority; "
                "the client checks the signature chain and that the certificate matches the hostname. The two sides then use a key exchange such as ECDHE to agree "
                "on fresh symmetric session keys, which encrypt and protect the rest of the traffic, including paths, headers and cookies."
            )),
        ],
        keyPoints=[
            "Resolution order on a cold cache: recursive resolver asks root, then TLD, then the authoritative server.",
            "Resolvers cache answers for the record's TTL, which is why DNS changes take time to spread.",
            "GET, PUT and DELETE are idempotent; POST is not, so retry it with care.",
            "401 means not authenticated; 403 means the server refuses, typically because you are authenticated but not permitted.",
            "TLS uses certificates to prove the server's identity and symmetric session keys to encrypt traffic.",
        ],
        challenges=[
            dict(id='challenge-cn-dns-http-q1', kind='prediction', title='Order of DNS queries',
                 prompt="A recursive resolver with an empty cache resolves www.example.com. In what order does it contact servers?",
                 options=["Authoritative server for example.com, then .com server, then root",
                          ".com server, then root, then authoritative server for example.com",
                          "Root, then .com server, then authoritative server for example.com"],
                 answer=2,
                 explanation="With nothing cached, the resolver starts at the top: the root refers it to the .com servers, and the .com server refers it to example.com's authoritative servers, which give the answer. It cannot start at the authoritative server because it does not yet know where that server is, and it learns where the .com servers are from the root.",
                 hint="Each server can only point you one level further down the name."),
            dict(id='challenge-cn-dns-http-q2', kind='prediction', title='Safe to retry',
                 prompt="A client's request times out and it does not know whether the server processed it. Which request can it resend without risking a different end result?",
                 options=["POST /orders with a new order",
                          "PUT /orders/42 with the complete order",
                          "PATCH /counter that adds 1 to a value"],
                 answer=1,
                 explanation="PUT is idempotent: replacing order 42 with the same full content twice leaves the same state as doing it once. Repeating the POST could create a second order, and a PATCH that adds 1 would add 2 if applied twice.",
                 hint="Ask what the server's state looks like if the request runs twice."),
            dict(id='challenge-cn-dns-http-q3', kind='prediction', title='Logged in but not allowed',
                 prompt="A user is logged in and sends a valid request to an admin-only page they have no rights to. Which status code fits best?",
                 options=["403 Forbidden", "401 Unauthorized", "404 Not Found", "500 Internal Server Error"],
                 answer=0,
                 explanation="The server knows who the user is but refuses the action, which is exactly 403. 401 means the request lacks valid authentication, which is not the case here. 404 is sometimes used to hide a page's existence but does not describe the situation, and 500 signals a server bug.",
                 hint="The server already knows who the user is."),
            dict(id='challenge-cn-dns-http-q4', kind='prediction', title='The stubborn old address',
                 prompt="You point your site's A record at a new server, but for about an hour some users still reach the old one. What is the most likely cause?",
                 options=["Browsers cached a 301 redirect to the old server",
                          "The TLS certificate is tied to the old IP address",
                          "Root servers only refresh their data once an hour",
                          "Resolvers cached the old A record and keep serving it until its TTL expires"],
                 answer=3,
                 explanation="Recursive resolvers cache each answer for the record's TTL, so anyone behind a resolver that cached the old address keeps getting it until the TTL runs out. A 301 points to URLs, not IP addresses; certificates are tied to hostnames, not IPs; and root servers only hold referrals to TLDs, not your A record.",
                 hint="Every DNS record carries a lifetime for caches."),
            dict(id='challenge-cn-dns-http-q5', kind='prediction', title='What TLS keys do',
                 prompt="In an HTTPS connection, what does the server's certificate do, and what encrypts the page data?",
                 options=["The certificate's public key encrypts every request and response",
                          "The certificate lets the client verify the server's identity, and symmetric session keys from the handshake encrypt the data",
                          "The certificate proves the client's identity, and data is sent unencrypted once the handshake succeeds"],
                 answer=1,
                 explanation="The certificate binds the server's public key to its hostname, signed by a trusted authority, so the client knows who it is talking to. The handshake then agrees symmetric keys, which are far faster for bulk encryption. Public-key operations are too slow for all traffic, and in normal HTTPS only the server presents a certificate and all application data stays encrypted.",
                 hint="Asymmetric crypto is slow; think about what it is used for only once."),
        ],
    ),
    dict(
        id='guide-cs-fundamentals-cn-network-security', kind='guide', track='cs-fundamentals', subject='Computer networks',
        title='Network security basics', order=6,
        summary="The goals of network security, how symmetric and asymmetric cryptography differ, the common attacks, and the layered defences against them.",
        sections=[
            dict(title='What security is trying to protect', text=(
                "Most security discussions start from three goals. Confidentiality means only the intended parties can read the data. Integrity means nobody can change "
                "it without being detected. Availability means the service stays usable for the people who should have it. Two more goals often join these: "
                "authentication, proving who someone is, and non-repudiation, making it hard to deny having sent something.\n\n"
                "It helps to link each goal to a tool. Encryption gives confidentiality. Hashes, message authentication codes and digital signatures give integrity, "
                "and signatures also give authentication. Redundancy, rate limiting and traffic filtering protect availability. In an interview, when you are asked "
                "about an attack, name which goal it breaks and which tool restores it. That shows you understand the idea rather than a list of terms."
            )),
            dict(title='Symmetric and asymmetric encryption', text=(
                "Symmetric encryption uses one shared key to encrypt and decrypt. AES is the standard example. It is fast, but the parties need a safe way to share the "
                "key, and the number of keys grows quickly: with n people who each need a private channel to everyone else, you need n(n-1)/2 keys, so 10 people need 45.\n\n"
                "Asymmetric encryption uses a key pair. Anyone can use the public key to encrypt a message that only the private key can decrypt. Reversed, the owner uses "
                "the private key to sign, and anyone can check the signature with the public key. RSA and elliptic-curve schemes are examples. Each person needs just one "
                "pair, but the operations are much slower.\n\n"
                "So real systems are hybrid: asymmetric crypto authenticates the parties and agrees a symmetric key, then symmetric crypto carries the data. TLS works this way. "
                "Hashing is different again: a one-way function like SHA-256 that cannot be reversed. Passwords should be stored with a salted, deliberately slow hash such as bcrypt or Argon2."
            )),
            dict(title='Common attacks', text=(
                "Eavesdropping, or sniffing, means reading traffic on a shared network; encryption is the answer. In a man-in-the-middle attack, the attacker sits between "
                "two parties, often by ARP spoofing on a LAN or running a fake Wi-Fi hotspot, and relays or alters messages. Encryption alone is not enough here; you also need "
                "authentication, which is why browsers check certificates.\n\n"
                "Denial of service tries to exhaust a resource. A SYN flood sends many SYNs, often from spoofed addresses, and never completes the handshake, filling the server's "
                "table of half-open connections. SYN cookies defend against this by not storing state until the final ACK arrives. A distributed attack uses many machines at once.\n\n"
                "DNS cache poisoning plants a forged answer in a resolver so users are sent to the wrong address; DNSSEC adds signatures to prevent it. Replay attacks resend "
                "captured valid messages, and nonces or timestamps stop them. Phishing tricks people rather than machines. On the web, also know SQL injection, cross-site scripting and cross-site request forgery by name."
            )),
            dict(title='Defences in layers', text=(
                "No single control is enough, so networks use defence in depth. A firewall filters traffic by rules on addresses, ports and protocols. A stateful firewall also "
                "tracks connections, so replies to traffic you started are let in while unsolicited inbound packets are dropped. Good rule sets deny by default and allow only what is needed.\n\n"
                "An intrusion detection system watches traffic and raises alerts on suspicious patterns; an intrusion prevention system sits inline and can block them. Public-facing "
                "servers are often placed in a DMZ, a separate segment, so a compromise there does not expose the internal network directly. A VPN builds an encrypted tunnel across "
                "an untrusted network, using IPsec at the network layer or TLS-based designs.\n\n"
                "Around these sit habits that stop most real incidents: patching, least privilege, multi-factor authentication, and logging that someone actually reviews."
            )),
        ],
        keyPoints=[
            "Confidentiality, integrity and availability are the core goals; map each attack to the goal it breaks.",
            "Symmetric crypto is fast but needs a shared key; n parties need n(n-1)/2 pairwise keys.",
            "Asymmetric crypto: encrypt with the recipient's public key, sign with your own private key.",
            "TLS is hybrid: asymmetric for authentication and key agreement, symmetric for the data.",
            "A SYN flood fills the half-open connection table; SYN cookies are the classic defence.",
            "Store passwords as salted slow hashes, never as plain or reversibly encrypted text.",
        ],
        challenges=[
            dict(id='challenge-cn-network-security-q1', kind='prediction', title='Counting shared keys',
                 prompt="Six people each want a private channel with every other person using only symmetric keys, one key per pair. How many keys are needed?",
                 options=["6", "12", "15", "30"],
                 answer=2,
                 explanation="Each pair needs one key, and the number of pairs among 6 people is 6 x 5 / 2 = 15. 30 counts each pair twice, 6 is the number of key pairs asymmetric crypto would need, and 12 has no basis.",
                 hint="Count unordered pairs of people."),
            dict(id='challenge-cn-network-security-q2', kind='prediction', title='Signing a message',
                 prompt="Alice wants to sign a message so that Bob can confirm it came from her. Which key does Alice use to create the signature?",
                 options=["Bob's public key", "Alice's private key", "Alice's public key", "Bob's private key"],
                 answer=1,
                 explanation="Only Alice holds her private key, so a signature made with it can only have come from her, and Bob checks it with her public key. Bob's public key is for encrypting messages to Bob, Alice's public key is known to everyone so it proves nothing, and Alice never has Bob's private key.",
                 hint="The signature must be something only Alice could produce."),
            dict(id='challenge-cn-network-security-q3', kind='prediction', title='Half-open connections',
                 prompt="A server's table of half-open TCP connections fills up with SYNs from many spoofed addresses that never send the final ACK. What attack is this?",
                 options=["SYN flood, a denial-of-service attack", "Man-in-the-middle", "DNS cache poisoning", "Replay attack"],
                 answer=0,
                 explanation="Sending SYNs without completing the handshake ties up server memory for each half-open connection until legitimate clients cannot connect, which is a SYN flood. A man-in-the-middle intercepts real traffic, cache poisoning targets DNS resolvers, and a replay resends captured valid messages.",
                 hint="Focus on which server resource is being used up and never released."),
            dict(id='challenge-cn-network-security-q4', kind='prediction', title='Why TLS is hybrid',
                 prompt="Why does TLS use asymmetric cryptography during the handshake but symmetric cryptography for the data?",
                 options=["Symmetric ciphers can only encrypt a single message",
                          "Asymmetric keys are too short to protect large data",
                          "Symmetric encryption cannot detect tampering",
                          "Asymmetric operations are much slower, so they are used to authenticate and agree a key that a fast symmetric cipher then uses"],
                 answer=3,
                 explanation="Public-key operations are expensive, so TLS uses them once to verify the server and agree on session keys, then switches to fast symmetric encryption for the bulk of the traffic. Symmetric ciphers handle unlimited messages, key length is not the reason (RSA keys, for example, are far longer than AES keys), and modern symmetric modes such as AES-GCM do detect tampering.",
                 hint="Think about cost per byte."),
            dict(id='challenge-cn-network-security-q5', kind='prediction', title='Storing passwords',
                 prompt="What is the right way for a server to store user passwords?",
                 options=["Encrypt them with AES and keep the key on the same server",
                          "Hash each one with a unique salt using a slow function such as bcrypt",
                          "Hash them with plain SHA-256 and no salt",
                          "Base64-encode them so they are not readable at a glance"],
                 answer=1,
                 explanation="A salted slow hash cannot be reversed, the salt stops precomputed tables and makes identical passwords hash differently, and the slowness makes brute force expensive. AES with the key on the same server is reversed as soon as the server is breached, unsalted fast SHA-256 is easy to attack with precomputed tables and fast guessing, and Base64 is just an encoding anyone can undo.",
                 hint="The server never needs to recover the original password, only check it."),
        ],
    ),
]
