#!/usr/bin/env python3
"""
make_sample.py - generate the sample capture.pcap for the pcap-http-extraction example.

Builds realistic traffic: a DNS lookup, two inconsequential HTTP page loads,
and one HTTP download of secret_note.txt containing the flag. Real challenge
pcaps are given to you; this generator only exists so the repo's walkthrough
is reproducible end-to-end.

Usage: python3 make_sample.py   (writes capture.pcap)
Requires: pip3 install scapy
"""

from scapy.all import IP, TCP, UDP, DNS, DNSQR, DNSRR, Raw, wrpcap

CLIENT, SERVER = "10.0.0.10", "10.0.0.20"
FLAG = "flag{h77p_obj3ct5_4r3_fr33}"

packets = []
ts = 1_700_000_000.0


def tick():
    global ts
    ts += 0.05
    return ts


def http_exchange(sport, path, host, response_body, content_type, filename=None, cseq=1000, sseq=9000):
    """A complete, if minimal, HTTP/1.1 session over its own TCP connection."""
    # handshake
    packets.append(IP(src=CLIENT, dst=SERVER) / TCP(sport=sport, dport=80, flags="S", seq=cseq))
    packets[-1].time = tick()
    packets.append(IP(src=SERVER, dst=CLIENT) / TCP(sport=80, dport=sport, flags="SA", seq=sseq, ack=cseq + 1))
    packets[-1].time = tick()
    packets.append(IP(src=CLIENT, dst=SERVER) / TCP(sport=sport, dport=80, flags="A", seq=cseq + 1, ack=sseq + 1))
    packets[-1].time = tick()

    # request
    req = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
           f"User-Agent: curl/7.88.1\r\nAccept: */*\r\n\r\n").encode()
    packets.append(IP(src=CLIENT, dst=SERVER) / TCP(sport=sport, dport=80, flags="PA", seq=cseq + 1, ack=sseq + 1) / Raw(req))
    packets[-1].time = tick()

    # response
    hdr = (f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n" +
           (f'Content-Disposition: attachment; filename="{filename}"\r\n' if filename else "") +
           f"Content-Length: {len(response_body)}\r\n\r\n").encode()
    packets.append(IP(src=SERVER, dst=CLIENT) / TCP(sport=80, dport=sport, flags="PA", seq=sseq + 1, ack=cseq + 1 + len(req)) / Raw(hdr + response_body))
    packets[-1].time = tick()

    # teardown (FIN/ACK both ways, abbreviated to one each for brevity)
    packets.append(IP(src=SERVER, dst=CLIENT) / TCP(sport=80, dport=sport, flags="FA", seq=sseq + 1 + len(hdr) + len(response_body), ack=cseq + 1 + len(req)))
    packets[-1].time = tick()
    packets.append(IP(src=CLIENT, dst=SERVER) / TCP(sport=sport, dport=80, flags="FA", seq=cseq + 1 + len(req), ack=sseq + 2 + len(hdr) + len(response_body)))
    packets[-1].time = tick()


# noise: DNS lookup for the intranet host
dns_q = IP(src=CLIENT, dst="10.0.0.53") / UDP(sport=5353, dport=53) / DNS(rd=1, qd=DNSQR(qname="intranet.corp.local"))
dns_q.time = tick()
packets.append(dns_q)
dns_a = IP(src="10.0.0.53", dst=CLIENT) / UDP(sport=53, dport=5353) / DNS(
    qr=1, qd=DNSQR(qname="intranet.corp.local"),
    an=DNSRR(rrname="intranet.corp.local", rdata=SERVER))
dns_a.time = tick()
packets.append(dns_a)

http_exchange(12345, "/index.html", "intranet.corp.local", b"<h1>Intranet</h1><p>nothing to see</p>", "text/html", cseq=1000, sseq=5000)
http_exchange(12347, "/assets/style.css", "intranet.corp.local", b"body { font-family: monospace; color: #333 }", "text/css", cseq=2000, sseq=7000)
http_exchange(12346, "/download/secret_note.txt", "intranet.corp.local",
              f"note to self: credentials moved to vault. {FLAG}".encode(),
              "text/plain", filename="secret_note.txt", cseq=3000, sseq=9000)

wrpcap("capture.pcap", packets)
print(f"[+] wrote capture.pcap with {len(packets)} packets (flag payload inside the :12346 stream)")
