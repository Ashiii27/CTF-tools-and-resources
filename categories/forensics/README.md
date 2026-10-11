# Forensics

> Recovering hidden, deleted, or buried evidence from files, disks, memory dumps, network captures, and logs. The most diverse CTF category — and the friendliest to newcomers.

---

## What Forensics Challenges Look Like

A forensics challenge hands you one or more **artifacts** — never a live server to "hack" — and asks you to dig information out of them. Typical challenge descriptions:

> *"We recovered this packet capture from a suspect's machine. Something was exfiltrated — find out what."*
> *"Our sysadmin accidentally deleted an important file from this disk image. Recover it."*
> *"This computer was acting strange before it crashed. We took a memory dump — find what the attacker ran."*
> *"The flag is somewhere in this file. Good luck."* (it's a 200 MB file of apparently random bytes)

The flag is almost always **evidence**: a deleted file's contents, a downloaded payload, a process that was running, a password typed into a login form, or data exfiltrated over the network.

## Subcategories

| Subcategory | Artifact you get | The job |
|---|---|---|
| **Network forensics** | `.pcap` / `.pcapng` | Follow streams, export transferred files, spot covert channels |
| **Disk forensics** | `.img` / `.dd` / `.E01` | Mount or parse the filesystem, recover deleted files, read artifacts |
| **Memory forensics** | `.raw` / `.dmp` / `.mem` | List processes/connections, dump process memory, find malware |
| **Log analysis** | `.evtx`, `auth.log`, `syslog`, web server logs | Correlate events to reconstruct what happened |
| **File carving / format tricks** | any file | Extract embedded data, repair truncated files, abuse format internals |
| **Metadata / document forensics** | images, PDFs, Office docs | EXIF, embedded objects, revision history, macros |
| **Mobile / OS artifacts** | Android backups, browser profiles | Databases (SQLite), caches, histories |

Steganography is adjacent but lives in its own category (`categories/stego/`).

## Recommended Learning Order

1. **File formats & signatures** — you'll identify files hundreds of times per event. Start with `quick-ref/magic-bytes.md` and the `file`/`xxd` workflow.
2. **Metadata & lightweight carving** — `exiftool`, `strings`, `binwalk -e`. Wins a large share of beginner challenges by itself.
3. **Network forensics** — Wireshark + tshark on pcaps. High challenge density, fast feedback. See `notes/network-forensics.md`.
4. **Log analysis** — grep/awk over Linux logs, then Windows Event Logs + event IDs. See `notes/log-analysis.md`.
5. **File carving properly** — foremost/scalpel configs, manual carving with `dd`. See `notes/file-carving.md`.
6. **Disk forensics** — mounting images, Sleuth Kit workflow, deleted file recovery. See `notes/disk-forensics.md`.
7. **Memory forensics** — Volatility 3 workflow. Steepest curve, biggest payoff in medium+ challenges. See `notes/memory-forensics.md`.
8. **Windows artifacts** — registry hives, prefetch, LNK, SRUM, amcache. See `notes/windows-artifacts.md`.

## Prerequisites

You should be comfortable with everything in these files *before* mid-level forensics:

- `fundamentals/linux-for-ctf.md` — `dd`, `mount`, `grep`, `awk`, `file`, `strings`, pipes
- `fundamentals/encoding-decoding.md` — exfiltrated data is almost always base64'd first
- `fundamentals/python-scripting.md` — for parsing anything nonstandard
- `quick-ref/magic-bytes.md` — printed, taped to your monitor

## The Forensics Mindset

- **Trust nothing you can't verify:** extensions lie, timestamps lie, filenames lie. Hex dumps don't.
- **Work on copies.** Always. `cp evidence.img work.img` before your first command, and hash the original.
- **The challenge tells you where to look:** "find what was downloaded" → network or browser artifacts. "what did the attacker run" → memory or prefetch. The question *is* the hint.
- **Deleted doesn't mean gone.** It's the entire premise of the category.

## First Tools to Learn

In order: `file`, `strings`, `xxd`, `exiftool`, `binwalk`, `wireshark`, `foremost`, `vol`. Full list with install commands in `tools.md`; dense one-liners in `cheatsheet.md`.

## Practice

- [picoGym Forensics](https://picoctf.org/) — the beginner ramp
- [CyberDefenders](https://cyberdefenders.org/) — realistic full-investigation labs ("blue team CTF")
- [MemLabs](https://github.com/stuxnet999/MemLabs) — memory forensics challenges, 6 progressive labs
- [HTB Sherlocks](https://www.hackthebox.com/) — narrative DFIR cases
- Any weekend CTF — forensics is usually the biggest category by challenge count

---

_Back to the [main roadmap](../../README.md)_
