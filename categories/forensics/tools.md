# Forensics Tools

> Every forensics tool worth having: install command, what it does, one example. Grouped by job. Install commands target Kali/Debian/Ubuntu; Kali already ships most of these.

---

## The Universal First Five

### file
Identifies file types by content (magic bytes), not extension.
```bash
sudo apt install file
file mystery.bin        # mystery.bin: PNG image data, 1920 x 1080...
```

### strings
Dumps printable ASCII/Unicode sequences — the fastest low-hanging-fruit check.
```bash
sudo apt install binutils          # strings lives here
strings -n 8 mem.raw | grep -i flag
```

### xxd
Hex dump your way into anything; `-r` also *reverses* a hex dump back to binary.
```bash
sudo apt install xxd
xxd suspicious.png | head -20
```

### exiftool
Read/write metadata of basically any file format (EXIF, XMP, ID3, doc props…).
```bash
sudo apt install libimage-exiftool-perl
exiftool holiday.jpg | grep -i -E 'comment|author|gps'
```

### binwalk
Signature scanner: finds embedded files/archives/compressed regions inside a blob.
```bash
sudo apt install binwalk
binwalk -eMe firmware.bin     # extract, recurse (-M), and extract those too (-e...again)
```

---

## File Carving

### foremost
Header/footer-based file carver that pulls files out of disk images and dumps.
```bash
sudo apt install foremost
foremost -i evidence.img -o carve_out/
```

### scalpel
Foremost's faster successor, driven by a config file of signatures.
```bash
sudo apt install scalpel
scalpel evidence.img -o scalpel_out/
```
Note: `/etc/scalpel/scalpel.conf` ships with **every file type commented out** — uncomment what you need first.

### bulk_extractor
Scans a disk image and auto-extracts "features": URLs, emails, credit cards, EXIF, ZIP offsets — without parsing the filesystem.
```bash
sudo apt install bulk-extractor
bulk_extractor -o bulk_out evidence.img
```

---

## Disk & Filesystem

### sleuthkit (TSK)
The CLI core of disk forensics: `mmls` (partitions), `fls` (files, incl. deleted), `icat` (recover by inode), `tsk_recover`, `istat`.
```bash
sudo apt install sleuthkit
mmls disk.img                    # partition table with sector offsets
fls -o 2048 -r -d disk.img       # list deleted files recursively
icat -o 2048 disk.img 9228 > recovered.zip   # carve file out by inode
```

### autopsy
GUI built on The Sleuth Kit — timeline views, deleted files, keyword search, ingest modules. The comfortable way through a big disk image.
```bash
sudo apt install autopsy
autopsy      # then open http://localhost:9999/autopsy
```

### ewf-tools
Mounts Expert Witness Format images (`.E01`), the standard forensic acquisition format.
```bash
sudo apt install ewf-tools
ewfmount image.E01 /mnt/ewf      # exposes a raw 'ewf1' you can then loop-mount
```

---

## Network

### wireshark
The packet-analysis GUI. Filters, stream following, object export, statistics.
```bash
sudo apt install wireshark
sudo usermod -aG wireshark $USER   # capture without root; re-login after
wireshark capture.pcap &
```

### tshark
Wireshark's CLI twin — same dissectors, scriptable. Everything in `cheatsheet.md` uses it.
```bash
sudo apt install tshark
tshark -r cap.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

### tcpdump
The minimal CLI capture/read tool; good on servers without a desktop.
```bash
sudo apt install tcpdump
tcpdump -nn -r cap.pcap 'tcp port 80' -A | head -50
```

### NetworkMiner
Extracts transferred files, images, credentials and host details from a pcap, GUI-style. Windows-friendly (runs under Mono on Linux).
```bash
# manual download — https://www.netresec.com/?page=NetworkMiner
mono NetworkMiner.exe            # on linux with mono installed
```

---

## Memory Forensics

### Volatility 3
THE memory forensics framework. Python 3, no profiles (symbols auto-downloaded). `windows.*`, `linux.*`, `mac.*` plugin families.
```bash
pip3 install --user --break-system-packages volatility3
# or better, isolated:  pipx install volatility3
vol -f memory.dmp windows.pslist
```
Full plugin cheat sheet: `cheatsheet.md`, full workflow: `notes/memory-forensics.md`.

---

## Password & Hash Cracking

(dumps and archives usually gate the flag behind a password)

### john (John the Ripper)
CPU hash cracker plus a family of `*2john` extractors (zip, rar, pdf, ssh, office…).
```bash
sudo apt install john
zip2john secret.zip > zip.hash && john --wordlist=/usr/share/wordlists/rockyou.txt zip.hash
```

### hashcat
GPU hash cracker — orders of magnitude faster when the wordlist/mask is right.
```bash
sudo apt install hashcat
hashcat -m 1800 shadow.hash /usr/share/wordlists/rockyou.txt
```

### fcrackzip
Dead-simple ZIP password brute-forcer; perfect when John feels heavy for a 3-char password.
```bash
sudo apt install fcrackzip
fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt secret.zip
```

---

## Logs & Timelines

### plaso (log2timeline)
Parses hundreds of artifact types into one giant super-timeline CSV/JSON.
```bash
sudo apt install plaso
log2timeline.py timeline.plaso disk.img && psort.py -o l2tcsv timeline.plaso > timeline.csv
```
Steep curve, massive power. Learn `grep`-on-timeline after you can build one.

### chainsaw
Rapid searching + hunting through Windows Event Logs (`.evtx`) with built-in Sigma support.
```bash
# prebuilt binaries — https://github.com/WithSecureLabs/chainsaw/releases
./chainsaw hunt /evidence/Logs/ -s sigma/ --mapping mappings/sigma-event-logs-all.yml
```

### hayabusa
Sigma-based threat hunting for Windows event logs with excellent built-in rules and HTML/CSV output.
```bash
# prebuilt binaries — https://github.com/Yamato-Security/hayabusa/releases
./hayabusa csv-timeline -d /evidence/Logs/ -o hayabusa.csv
```

### Eric Zimmerman's Tools
The industry-standard Windows artifact parsers: **MFTECmd** ($MFT), **PECmd** (prefetch), **LECmd** (LNK), **AmcacheParser**, **EvtxECmd**, **RegistryExplorer/RECmd**, **KAPE** (collector/executor that runs them all). Windows-only (.NET); run from a Windows VM or grab-and-analyze offline.
```powershell
# download bundle — https://ericzimmerman.github.io/  (Get-ZimmermanTools script)
MFTECmd.exe -f 'C:\evidence\$MFT' --csv out\
PECmd.exe -d 'C:\evidence\Prefetch' --csv out\
```
Linux alternative for quick peeks: `pip install regipy` for hives.

---

## Mobile / Browser (bonus)

| Tool | Install | Job |
|---|---|---|
| `sqlite3` | `sudo apt install sqlite3` | Open app/browser DBs: `sqlite3 places.sqlite 'select url,title from moz_places'` |
| ALEAPP / iLEAPP | `pip install aleapp` / `pip install ileapp` | Parse full Android / iOS extractions into reports |
| sqlitebrowser | `sudo apt install sqlitebrowser` | GUI browsing of SQLite files |

---

_Back to the [main roadmap](../../README.md)_
