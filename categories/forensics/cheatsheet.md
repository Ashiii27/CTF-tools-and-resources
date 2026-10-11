# Forensics Cheat Sheet

> Single-page quick reference: tshark one-liners, Volatility 3 plugins, carving commands, log grep patterns, magic bytes. Dense by design — explanations live in `notes/`.

---

## tshark One-Liners (pcap)

```bash
# ---- overview ----
tshark -r cap.pcap -q -z io,phs                          # protocol hierarchy (what's in here?)
tshark -r cap.pcap -q -z conv,tcp                        # TCP conversations, sorted by size
tshark -r cap.pcap -q -z conv,ip                         # IP conversations
tshark -r cap.pcap -q -z endpoints,ip                    # all IPs seen
tshark -r cap.pcap -q -z expert                          # anomalies spotted by dissectors

# ---- inspect fields ----
tshark -r cap.pcap -Y 'http.request' -T fields -e frame.number -e ip.src -e http.host -e http.request.method -e http.request.uri
tshark -r cap.pcap -Y 'http' -T fields -e http.user_agent | sort -u          # user-agents
tshark -r cap.pcap -Y 'dns' -T fields -e dns.qry.name | sort -u              # every DNS query
tshark -r cap.pcap -Y 'dns.txt' -T fields -e dns.txt                         # TXT records (tunneling!)
tshark -r cap.pcap -Y 'http.response.code == 200 && http.content_type contains "application"' -T fields -e http.request.uri
tshark -r cap.pcap -Y 'http.cookie' -T fields -e http.cookie_pair            # cookies

# ---- flag hunting ----
tshark -r cap.pcap -Y 'frame contains "flag"'
tshark -r cap.pcap -Y 'frame contains "CTF{"' -T fields -e frame.number -e tcp.stream
tshark -r cap.pcap -Y 'data-text-lines contains "flag"' -T fields -e frame.number

# ---- credentials ----
tshark -r cap.pcap -Y 'ftp.request.command == "USER" || ftp.request.command == "PASS"' -T fields -e ftp.request.arg
tshark -r cap.pcap -Y 'http.authbasic' -T fields -e http.authbasic           # basic-auth (b64 of user:pass)
tshark -r cap.pcap -Y 'http.request.method == "POST"' -T fields -e urlencoded-form.key -e urlencoded-form.value

# ---- stream following ----
tshark -r cap.pcap -q -z follow,tcp,ascii,0              # TCP stream 0 as ASCII
tshark -r cap.pcap -q -z follow,tcp,raw,0                # raw hex of stream 0 (pipe to xxd -r)
tshark -r cap.pcap -q -z follow,udp,ascii,0
tshark -r cap.pcap -q -z 'follow,tcp,ascii,0' | sed -n '/^=/,$p'

# ---- export transferred files ----
tshark -r cap.pcap --export-objects http,outdir          # ALL http objects into outdir/
tshark -r cap.pcap --export-objects smb,outdir           # SMB files
tshark -r cap.pcap --export-objects imf,outdir           # email attachments
tshark -r cap.pcap --export-objects tftp,outdir

# ---- DNS tunneling quick check ----
tshark -r cap.pcap -Y 'dns' -T fields -e dns.qry.name | awk '{print length, $0}' | sort -rn | head

# ---- carve payloads manually from a stream ----
tshark -r cap.pcap -Y 'tcp.stream eq 3' -T fields -e tcp.payload | tr -d '\n' | xxd -r -p > stream3.bin
```

## Wireshark Display Filters

```text
ip.addr == 10.0.0.5                 host either direction
tcp.stream eq 4                     one whole conversation
http.request / http.response
dns.qry.name contains "exfil"
frame contains "password"
tcp.flags.syn==1 && tcp.flags.ack==0    all connection attempts (scan detection)
data.data matches "(?i)flag\{"
!(arp || dns || icmp)               quiet the noise
smb2.cmd == 5                       SMB2 file reads (5=READ)
```

## Volatility 3 Cheat Sheet

```bash
# ---- identify ----
vol -f mem.dmp windows.info                       # vol3 has NO profiles / NO imageinfo
vol -f mem.dmp banners.Banners                    # linux/mac image hints

# ---- processes ----
vol -f mem.dmp windows.pslist
vol -f mem.dmp windows.pstree                     # parent/child — svchost spawned by NOT services.exe = bad
vol -f mem.dmp windows.psscan                     # finds unlinked/hidden processes pslist misses
vol -f mem.dmp windows.cmdline                    # full command lines — often the flag itself
vol -f mem.dmp windows.envars --pid 1337          # environment of one process
vol -f mem.dmp windows.getsids --pid 1337         # which user/SID owned it

# ---- network ----
vol -f mem.dmp windows.netscan                    # connections/listeners w/ owning PID
vol -f mem.dmp windows.netstat

# ---- files & dumpers ----
vol -f mem.dmp windows.filescan | grep -i -E 'flag|secret|\.zip'
vol -f mem.dmp windows.dumpfiles --pid 1337                     # files cached for that process
vol -f mem.dmp windows.dumpfiles.DumpFiles --physaddr 0xXXXX    # by physical offset (from filescan)
vol -f mem.dmp windows.memmap --pid 1337 --dump                 # FULL process memory dump → then strings
vol -f mem.dmp windows.malfind --dump                           # injected code regions (RWX VADs)

# ---- registry / creds ----
vol -f mem.dmp windows.hivelist
vol -f mem.dmp windows.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
vol -f mem.dmp windows.hashdump                   # local account hashes (needs SYSTEM+SAM in memory)
vol -f mem.dmp windows.lsadump                    # LSA secrets
vol -f mem.dmp windows.cachedump                  # domain cached creds

# ---- misc winners ----
vol -f mem.dmp windows.dlllist --pid 1337
vol -f mem.dmp windows.handles --pid 1337
vol -f mem.dmp windows.cmdline | grep -i -E 'flag|pass|\.py'
vol -f mem.dmp windows.sessions
vol -f mem.dmp windows.svcscan                    # services

# ---- linux dumps ----
vol -f mem.dmp linux.pslist.PsList
vol -f mem.dmp linux.bash.Bash                    # bash history from memory — CTF gold
vol -f mem.dmp linux.lsof.Lsof --pid 1337
vol -f mem.dmp linux.envars.Envars

# ---- universal fallback ----
strings mem.dmp | grep -i -E 'flag\{|ctf\{|htb\{'
```

## File Carving

```bash
# ---- auto ----
binwalk -eMe file.bin                              # sig scan + recursive extract
binwalk -E file.bin                                # entropy analysis (finds packed/encrypted blobs)
foremost -i evidence.img -o out/ -v
foremost -t zip,png,pdf -i evidence.img -o out/    # selected types only
scalpel evidence.img -o out/                       # EDIT /etc/scalpel/scalpel.conf FIRST (all commented!)
bulk_extractor -o bulk_out evidence.img            # URLs/emails/cards/zip-offsets features

# ---- manual carve by offsets (from binwalk/xxd) ----
xxd file.bin | grep -i '504b0304'                  # find PK.. (zip) offsets
dd if=file.bin of=carved.zip bs=1 skip=13371337 status=progress
python3 -c "d=open('file.bin','rb').read(); open('carved.png','wb').write(d[d.find(b'\x89PNG'):])"

# ---- repair ----
printf '\x49\x45\x4e\x44\xae\x42\x60\x82' >> broken.png       # append missing PNG IEND
zip -FF broken.zip --out fixed.zip                  # rebuild zip central directory
```

## Mounting Disk Images

```bash
mmls disk.img                                      # note partition START sectors
sudo mount -o ro,loop,offset=$((2048*512)) disk.img /mnt/img    # start*512 = byte offset
sudo losetup -fP --show disk.img && sudo mount -o ro /dev/loop0p1 /mnt/img
ewfmount image.E01 /mnt/ewf && sudo mount -o ro,loop /mnt/ewf/ewf1 /mnt/img
tsk_recover -e disk.img recovered/                 # sleuthkit: dump ALL files incl. deleted
fls -o 2048 -r -d disk.img                         # deleted file listing
```

## Log Grep Patterns

```bash
# ---- linux auth.log / syslog ----
grep -E 'Failed password|Invalid user' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn   # attacking IPs
grep 'Accepted' auth.log                           # successful logins
grep -E 'sudo:.*COMMAND' auth.log                  # what got sudo'd
grep -E 'useradd|adduser' syslog auth.log          # account creation
grep -E 'session opened for user root' auth.log    # root sessions

# ---- web access.log ----
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head        # top talkers
grep -iE 'user-agent.*(sqlmap|nikto|nmap|hydra|gobuster|dirbuster)' access.log
grep -iE '(union.*select|\.\.\/|\{\{.*\}\}|%27|<script)' access.log    # sqli/lfi/ssti/xss probes
awk '$9==200 {print $7}' access.log | grep -iE 'shell|cmd|upload'      # webshell hits

# ---- evtx quick hunt (chainsaw/hayabusa) ----
chainsaw search '*.evtx' -q 'EventID: 4625'
hayabusa csv-timeline -f Security.evtx -o out.csv
```

## Key Windows Event IDs

| ID | Log | Meaning |
|---|---|---|
| 4624 | Security | Logon success (Type 3=network, 10=RDP, 2=console) |
| 4625 | Security | Logon FAILURE (0xC000006A bad pass / 0xC0000064 no user) |
| 4648 | Security | Explicit credentials used (runas / lateral) |
| 4672 | Security | Special privileges assigned (admin-equivalent logon) |
| 4688 | Security | Process created (cmdline if auditing enabled) |
| 4698 | Security | Scheduled task created |
| 4720 | Security | User account created |
| 4726 | Security | User account deleted |
| 4732 | Security | Added to local group |
| 4740 | Security | Account lockout |
| 1102 | Security | **Log cleared** — huge red flag |
| 7045 | System | New service installed (classic persistence) |
| Sysmon 1/3/11/22 | Sysmon | Process create / network / file create / DNS query |

## Magic Bytes (top-of-mind)

```text
89 50 4E 47        PNG        50 4B 03 04     ZIP (and docx/apk/jar)
FF D8 FF           JPEG       25 50 44 46     %PDF
52 61 72 21        RAR        1F 8B           GZIP
7F 45 4C 46        ELF        4D 5A           PE (exe/dll)
D4 C3 B2 A1        pcap (LE)  0A 0D 0D 0A     pcapng
D0 CF 11 E0        OLE2/CFB (doc/xls/msg)     SQLite format 3\0 → sqlite3
```

Full table: `quick-ref/magic-bytes.md`

---

_Back to the [main roadmap](../../README.md)_
