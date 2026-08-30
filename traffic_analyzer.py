"""C4: opt-in local-interface packet composition and top-talker analysis."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass


@dataclass
class CaptureSummary:
    protocols: dict[str, tuple[int, int]]
    talkers: list[tuple[str, int]]
    warning: str | None = None


def capture_traffic(interface: str, seconds: int, count: int) -> CaptureSummary:
    """Capture a bounded amount of traffic; report permission problems instead of crashing."""
    try:
        from scapy.all import ARP, DNS, ICMP, IP, TCP, UDP, sniff
        packets = sniff(iface=interface, timeout=seconds, count=count, store=True)
    except Exception as error:
        return CaptureSummary({}, [], f"Capture unavailable: {error}. On Windows, install Npcap and run an elevated terminal if required.")
    protocol_counts: Counter = Counter()
    protocol_bytes: Counter = Counter()
    talkers: Counter = Counter()
    for packet in packets:
        label = "Other"
        if packet.haslayer(ARP): label = "ARP"
        elif packet.haslayer(DNS): label = "DNS"
        elif packet.haslayer(ICMP): label = "ICMP"
        elif packet.haslayer(TCP): label = "HTTP/HTTPS" if packet[TCP].sport in (80, 443) or packet[TCP].dport in (80, 443) else "TCP"
        elif packet.haslayer(UDP): label = "UDP"
        size = len(packet)
        protocol_counts[label] += 1; protocol_bytes[label] += size
        if packet.haslayer(IP):
            talkers[packet[IP].src] += size; talkers[packet[IP].dst] += size
    return CaptureSummary({name: (protocol_counts[name], protocol_bytes[name]) for name in
                          ("TCP", "UDP", "ICMP", "ARP", "DNS", "HTTP/HTTPS", "Other") if protocol_counts[name]}, talkers.most_common(10))
