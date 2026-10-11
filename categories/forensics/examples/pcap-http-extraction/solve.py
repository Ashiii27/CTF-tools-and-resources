#!/usr/bin/env python3
"""
solve.py - automated solve for the "Data Snatchers" pcap-http-extraction example.

Extracts every HTTP response body from a pcap by reassembling TCP streams
(scapy), saves them as files, and hunts for a flag pattern in each.

Usage:
    python3 solve.py capture.pcap
    python3 solve.py capture.pcap -o outdir --flag-regex 'CTF\\{[^}]*\\}'

No pcap-library magic beyond parsing: this works even when
`tshark --export-objects` fails (chunked encoding, odd ports, HTTP/0.9-ish
replies), which is exactly why it's worth having in your pocket.
"""

import argparse
import os
import re
import sys
from collections import defaultdict

try:
    from scapy.all import TCP, rdpcap
except ImportError:
    sys.exit("[x] scapy not installed: pip3 install scapy")

CRLF2 = b"\r\n\r\n"


def reassemble_streams(packets):
    """Concatenate TCP payloads per (src,dst,sport,dport), ordered by seq."""
    streams = defaultdict(list)  # flow -> [(seq, payload_bytes)]
    for pkt in packets:
        if pkt.haslayer(TCP) and pkt[TCP].payload:
            tcp = pkt[TCP]
            flow = (pkt["IP"].src, tcp.sport, pkt["IP"].dst, tcp.dport)
            channels = {
                # data direction: seq tracks bytes in this direction
                "a": tcp.seq,
                # pure SYN/FIN/ACK control packets carry no payload, ignore
            }
            payload = bytes(tcp.payload)
            if payload:
                streams[flow].append((channels["a"], payload))
    return {
        flow: b"".join(p for _, p in sorted(chunks))
        for flow, chunks in streams.items()
    }


def parse_http_responses(streams):
    """Yield (server_ip, filename, body) for each HTTP response found."""
    for (src, sport, dst, dport), data in streams.items():
        if sport != 80 and not data.startswith(b"HTTP/"):
            continue  # only server-side streams
        if CRLF2 not in data:
            continue
        headers_raw, body = data.split(CRLF2, 1)
        if not headers_raw.startswith(b"HTTP/"):
            continue
        headers = {
            k.strip().lower(): v.strip()
            for k, v in (line.split(b":", 1) for line in headers_raw.split(b"\r\n") if b":" in line)
        }
        # filename: Content-Disposition first, then request path
        fname = None
        cd = headers.get(b"content-disposition", b"")
        m = re.search(rb'filename="?([^";]+)"?', cd)
        if m:
            fname = m.group(1).decode(errors="replace")
        else:
            # find the matching request stream (same connection, reverse
            # direction -> compare IPs AND ports) to reuse its URL path
            for (csrc, csport, cdst, cdport), cdata in streams.items():
                if (csrc, csport, cdst, cdport) == (dst, dport, src, sport) and b"\r\n" in cdata:
                    first = cdata.split(b"\r\n", 1)[0]
                    m2 = re.match(rb"(?:GET|POST)\s+(\S+)", first)
                    if m2:
                        fname = m2.group(1).decode(errors="replace").strip("/").replace("/", "_")
                    break
        if not fname:
            fname = f"response_{src}_{sport}"
        yield src, fname, body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcap", help="input pcap file")
    ap.add_argument("-o", "--outdir", default="objects")
    ap.add_argument("--flag-regex", default=r"flag\{[^}]*\}")
    args = ap.parse_args()

    packets = rdpcap(args.pcap)
    print(f"[*] parsed {len(packets)} packets")

    os.makedirs(args.outdir, exist_ok=True)
    streams = reassemble_streams(packets)
    flag_re = re.compile(args.flag_regex.encode())

    found_flag = False
    for server_ip, fname, body in parse_http_responses(streams):
        safe = os.path.basename(fname)
        path = os.path.join(args.outdir, safe)
        with open(path, "wb") as f:
            f.write(body)
        print(f"[+] extracted -> {path} ({len(body)} bytes, served by {server_ip})")
        hit = flag_re.search(body)
        if hit:
            found_flag = True
            print(f"\n[+] FLAG FOUND in {safe}:")
            print(f"    {hit.group().decode(errors='replace')}\n")

    if not found_flag:
        print("[*] no flag pattern matched - check objects/ manually "
              "(or loosen --flag-regex)")


if __name__ == "__main__":
    main()
