# Solve: Data Snatchers

> Walkthrough for `challenge.md`. Three ways in — manual tshark, pure-python, and the one-liner export — because pcap challenges should never take more than five minutes.

---

## Step 0 — Generate the sample capture (repo example only)

```bash
pip3 install scapy
python3 make_sample.py        # → capture.pcap
```

In a real event you'd skip this; the organizers hand you the pcap.

## Step 1 — Orient: what's even in here?

```bash
tshark -r capture.pcap -q -z io,phs
```

```text
===================================================================
Protocol Hierarchy Statistics
Filter:
eth                                      frames:14 bytes:1456
  ip                                     frames:14 bytes:1456
    tcp                                  frames:13 bytes:1434
      http                               frames:6 bytes:1069
        data-text-lines                  frames:3 bytes:702
    udp                                  frames:1 bytes:22
      dns                                frames:1 bytes:22
===================================================================
```

HTTP with response bodies. Next question: who talked to whom, and how much went over it?

```bash
tshark -r capture.pcap -q -z conv,tcp
```

```text
================================================================================
TCP Conversations
Filter:<No Filter>
                                                          |       <-      | |       ->      |
10.0.0.10:12346          10.0.0.20:80                       39      400        258    404       297     804
10.0.0.10:12345          10.0.0.20:80                       24      200        150    210       174     410
10.0.0.10:12347          10.0.0.20:80                       18      140         98    180       116     320
================================================================================
```

Three HTTP conversations; the middle one (`:12346`) moved the most data back from the server.

## Step 2 — List every HTTP request

```bash
tshark -r capture.pcap -Y 'http.request' -T fields -e frame.number -e ip.src -e http.host -e http.request.method -e http.request.full_uri
```

```text
5    10.0.0.10    intranet.corp.local    GET    http://intranet.corp.local/index.html
9    10.0.0.10    intranet.corp.local    GET    http://intranet.corp.local/assets/style.css
12   10.0.0.10    intranet.corp.local    GET    http://intranet.corp.local/download/secret_note.txt
```

`secret_note.txt` doesn't belong on an intranet index page. That's our exfil channel.

## Step 3 — Read the transfer (three ways, pick any)

**Way A — follow the stream:**

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,1
```

```text
===================================================================
Follow: tcp,ascii
Filter: tcp.stream eq 1
Node 0: 10.0.0.10:12346
Node 1: 10.0.0.20:80
173
GET /download/secret_note.txt HTTP/1.1
Host: intranet.corp.local
User-Agent: curl/7.88.1
Accept: */*

        458
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Disposition: attachment; filename="secret_note.txt"
Content-Length: 74

note to self: credentials moved to vault. flag{h77p_obj3ct5_4r3_fr33}
===================================================================
```

**Way B — the cheat code (export every HTTP object):**

```bash
tshark -r capture.pcap --export-objects http,objects
find objects -type f -exec file {} \;
grep -ri 'flag{' objects/
```

```text
objects/secret_note.txt: ASCII text
objects/secret_note.txt:note to self: credentials moved to vault. flag{h77p_obj3ct5_4r3_fr33}
```

**Way C — automated solve script** (the one in this repo):

```bash
python3 solve.py capture.pcap
```

```text
[*] parsed 23 packets
[+] extracted -> objects/index.html (38 bytes, served by 10.0.0.20)
[+] extracted -> objects/assets_style.css (44 bytes, served by 10.0.0.20)
[+] extracted -> objects/secret_note.txt (69 bytes, served by 10.0.0.20)

[+] FLAG FOUND in secret_note.txt:
    flag{h77p_obj3ct5_4r3_fr33}
```

(That transcript is the script's real output against the generated sample capture; tshark transcripts above are representative — packet/byte counts differ slightly by tool version.)

## Flag

```text
flag{h77p_obj3ct5_4r3_fr33}
```

## Lessons Learned

1. **Conversations table first** — the biggest transfer is almost always the interesting one.
2. `--export-objects http,dir` is a one-command solution for a whole class of pcap challenges; reach for it before writing any code.
3. When objects don't export (chunked encoding, nonstandard ports, HTTP/2), fall back to stream reassembly — that's exactly what `solve.py` does, and the same logic ports to FTP/SMB/custom protocols.
4. `curl` in the user-agent on a "browsing the intranet" claim = case closed.
