# Network Forensics (pcap Analysis)

> A repeatable methodology for `.pcap`/`.pcapng` challenges: get oriented, follow the traffic, export the goods, and recognize the covert channels CTFs love. Assumes comfort with Linux and basic networking.

---

## The Methodology (in order)

A packet capture is haystack-shaped. These five steps find the needle systematically:

1. **Orient:** what protocols are even in here, and who's talking?
2. **Inventory:** list the interesting conversations and transfers.
3. **Extract:** follow streams, export files/objects.
4. **Decode:** the exfiltrated data is almost always encoded or chopped up.
5. **Hunt anomalies** when nothing obvious shows: DNS tunnels, ICMP payloads, timing tricks.

## Step 1 — Orient

```bash
tshark -r cap.pcap -q -z io,phs        # protocol hierarchy: "80% TCP, 15% DNS, ..."
tshark -r cap.pcap -q -z endpoints,ip  # every IP in the capture
tshark -r cap.pcap -q -z conv,tcp      # conversations sorted by byte count ← biggest first = exfil?
tshark -r cap.pcap -q -z expert        # retransmissions, malformed packets, dissector warnings
```

In Wireshark: `Statistics → Protocol Hierarchy`, `Statistics → Conversations`, sort by **Bytes**. If a capture is 90% of something unusual (DNS? ICMP?), that *is* the challenge.

## Step 2 — Inventory the Interesting Traffic

```bash
# everything requested over HTTP, with hosts and paths
tshark -r cap.pcap -Y 'http.request' -T fields -e frame.number -e ip.src -e http.host -e http.request.method -e http.request.uri

# who and what over DNS
tshark -r cap.pcap -Y 'dns' -T fields -e dns.qry.name | sort -u

# user agents (tools stand out: sqlmap, curl, EvilUploader/1.0)
tshark -r cap.pcap -Y 'http' -T fields -e http.user_agent | sort -u
```

Wireshark equivalents: type `http.request` or `dns` in the filter bar.

## Step 3 — Follow Streams and Export Files

**Streams** are Wireshark/tshark reassembling a whole conversation for you:

```bash
tshark -r cap.pcap -q -z follow,tcp,ascii,0     # TCP stream 0, human readable
tshark -r cap.pcap -q -z follow,udp,ascii,0
```

In Wireshark: right-click any packet → **Follow → TCP Stream**. You can page through streams with the "Stream" counter at the bottom of that window. This is where cleartext credentials and downloaded-file contents usually show up.

**Export transferred files** — the single most productive command in the pcap category:

```bash
tshark -r cap.pcap --export-objects http,outdir     # every HTTP-transferred file
tshark -r cap.pcap --export-objects smb,outdir      # SMB-transferred files
ls -la outdir && file outdir/*
```

Wireshark GUI equivalent: `File → Export Objects → HTTP…`. If export-objects yields nothing but you *see* a transfer in a stream, pull the raw payload yourself:

```bash
# all payload bytes of one stream, concat'd hex → binary
tshark -r cap.pcap -Y 'tcp.stream eq 3' -T fields -e tcp.payload | tr -d '\n' | xxd -r -p > stream3.bin
file stream3.bin          # usually: ZIP/PNG/PDF data ← binwalk it next
```

## Step 4 — Decode What You Extracted

Capture traffic is full of encodings-on-purpose: base64 blobs in POST bodies, hex in URL parameters, data split one character per DNS label. Jump to `fundamentals/encoding-decoding.md` — and try CyberChef's **Magic** operation on any opaque string.

## Step 5 — Covert Channels & Anomalies (the CTF greatest hits)

| Pattern | What it looks like | How to confirm |
|---|---|---|
| **DNS tunneling** | Hundreds of queries, absurdly long labels, high-entropy names (`aG9sYQ.evil.co`), many TXT | `tshark -Y 'dns' -T fields -e dns.qry.name \| awk '{print length, $0}' \| sort -rn \| head` — then concat labels and base64-decode |
| **ICMP exfil** | Ping flood with fat payloads | `-Y 'icmp' -T fields -e data.data`, `xxd -r -p` the concat |
| **HTTP exfil** | Small POSTs, same endpoint, base64 bodies | follow the stream; look at `urlencoded-form.value` |
| **Cleartext creds** | FTP `USER`/`PASS`, HTTP basic auth, form posts | `-Y 'ftp.request.command == "PASS"' -T fields -e ftp.request.arg`; `-Y 'http.authbasic'` (decode the b64) |
| **Slow beacon** | Same-size connections at rigid intervals | `-q -z conv,tcp` low byte counts, or plot with `Statistics → I/O Graph` filtered to the host |
| **Data in padding/metadata** | flags in HTTP headers/cookies | `-Y 'http.cookie' -T fields -e http.cookie_pair`; check `Server`/custom `X-` headers |
| **Stego-adjacent** | a transferred image/audio that *itself* hides data | export the object, then it's a stego challenge (`zsteg`, spectrogram) |
| **TLS you can't read** | everything encrypted | look for a supplied key log (`SSLKEYLOGFILE`) or a self-signed-cert hint; Wireshark: `Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename` |

## Protocols to Know Cold for CTF

| Protocol | Why it's in challenges |
|---|---|
| **HTTP** | object export, form creds, API exfil — accounts for most pcap challenges |
| **DNS** | #1 covert channel; subdomains carry data |
| **FTP** | cleartext auth + file transfers (`RETR secret.zip` reveals name *and* content via data channel) |
| **ICMP** | ping-payload exfiltration |
| **TCP raw** | custom protocols you must reassemble from streams |
| **SMB** | file shares: what was read/copied off |
| **SMTP/IMAP** | exfil by email; `--export-objects imf` |
| **IRC/Telnet** | ancient, cleartext, read it in `follow` like a novel |

Wireshark filter-bar quick list: `http` · `dns` · `ftp` · `tcp.stream eq N` · `ip.addr == 10.0.0.5` · `frame contains "flag"` · `!(arp || dns || icmp)` to silence noise.

## Worked Reference

A complete HTTP-extraction walkthrough with a solve script lives in `../examples/pcap-http-extraction/`.

---

_Back to the [main roadmap](../../../README.md)_
