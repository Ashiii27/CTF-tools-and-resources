# CTF Platforms

> Every platform worth knowing, sorted by *what it's for*: guided learning, open practice pools, and live competition. Per-category ranked shortlists at the bottom.

Cost legend: **Free** = everything free · **Freemium** = solid free tier + paid content · **Paid** = subscription required for the good stuff.

---

## 1. Learning Platforms (Guided Teaching)

Structured paths that teach before they test. Start here when a category is new to you.

| Platform | Teaches | Cost | Notes |
|---|---|---|---|
| [TryHackMe](https://tryhackme.com/) | Everything; guided rooms with in-browser VMs | Freemium | Best absolute-beginner on-ramp; Pre-Security → Jr Penetration Tester paths |
| [PortSwigger Web Security Academy](https://portswigger.net/web-security) | Web security, thoroughly | Free | The best web resource that exists, written by the Burp team; ~250 labs |
| [pwn.college](https://pwn.college/) | Systems security: asm, pwn, RE, sandboxing | Free | Real university course (ASU) with auto-graded challenges; "dojos" per topic |
| [CryptoHack](https://cryptohack.org/) | Modern cryptography | Free | Progressive quiz-style challenges from "what is ASN.1" to lattices |
| [Roppers Academy](https://www.roppers.org/) | Computing & pwn fundamentals | Free | Course materials + Discord community, aimed at real beginners |
| [HTB Academy](https://academy.hackthebox.com/) | Pentesting methodology, job-role paths | Freemium | More formal/HR-recognized than HTB main platform; cubes currency |
| [Exploit Education](https://exploit.education/) | Memory corruption (Phoenix/Protostar/Nebula VMs) | Free | Old but gold for stack/heap/format-string basics |
| [PentesterLab](https://pentesterlab.com/) | Web exploitation | Freemium | Curated badges from real CVEs; pro tier is strong |
| [OverTheWire](https://overthewire.org/wargames/) | Linux (Bandit), web (Natas), crypto (Krypton) | Free | The classic SSH wargames; everyone plays Bandit at level 0 |
| [Nightmare](https://guyinatuxedo.github.io/) | Binary exploitation course via CTF challenges | Free | Learn pwn by doing documented CTF writeups in order |

## 2. Practice Platforms (Open Challenge Pools)

Unstructured challenges at all difficulties — your gym between events.

| Platform | Focus | Cost | Notes |
|---|---|---|---|
| [picoCTF / picoGym](https://picoctf.org/) | All categories | Free | Beginner-friendly year-round gym from CMU; ~300 challenges |
| [CTFlearn](https://ctflearn.com/) | All categories | Free | Community-submitted challenges; quality varies, difficulty filter helps |
| [RootMe](https://www.root-me.org/) | All categories, 400+ challenges | Freemium | Huge depth in web/app-script/cracking; remote environments per challenge |
| [247CTF](https://247ctf.com/) | All categories, year-round scoreboard | Free | Fixed challenge set + own rating system; good pacing |
| [RingZer0 CTF](https://ringzer0ctf.com/) | All categories | Free | Lots of stego/crypto; some challenges are dated but instructive |
| [crackmes.one](https://crackmes.one/) | Reverse engineering only | Free | Thousands of user-submitted crackmes, difficulty-rated |
| [reversing.kr](http://reversing.kr/) | Reverse engineering | Free | Short, punchy RE ladder |
| [pwnable.kr](http://pwnable.kr/) | Pwn | Free | Classic; starts at "fd" and ends at kernel exploitation |
| [pwnable.xyz](https://pwnable.xyz/) | Pwn | Free | Web-based, rated challenges, no VM needed |
| [ROP Emporium](https://ropemporium.com/) | Return-oriented programming, one technique at a time | Free | The place to master ret2win → ret2csu systematically |
| [Microcorruption](https://microcorruption.com/) | Embedded RE in the browser | Free | Charming MSP430 lock-picking wargame; teaches real RE thinking |
| [Cryptopals](https://cryptopals.com/) | Crypto, implemented by you | Free | 8 sets of "build the attack" challenges; huge resume signal |
| [Hack The Box](https://www.hackthebox.com/) | Realistic vulnerable machines + challenge tracks | Freemium | The standard for boot2root; starting-point machines are beginner-safe |
| [VulnHub](https://www.vulnhub.com/) | Offline vulnerable VMs | Free | Download and attack locally; no account needed |
| [CyberDefenders](https://cyberdefenders.org/) | Blue team / DFIR | Freemium | Realistic forensic investigation labs (pcap, memory, disk) |
| [Blue Team Labs Online](https://blueteamlabs.online/) | DFIR, SOC, IR | Freemium | Good complement to CyberDefenders |
| [HackThisSite](https://www.hackthissite.org/) | Web/JS missions | Free | Ancient but the "basic" missions still teach fundamentals |
| [W3Challs](https://w3challs.com/) / [Root-Me] | Mixed | Free | Older European sites with unique challenge styles |

## 3. Competition (Live Events)

- **[CTFtime](https://ctftime.org/)** — the calendar and world ranking. Filter *Upcoming* by difficulty/weight; register a team, track your global rating.
- **Beginner-friendly recurring events:** picoCTF (CMU, spring), Google CTF Beginners Quest, CSAW Quals (students), PatriotCTF, UMass CTF, DiceCTF (open, with an easy track).
- **High-prestige events (watch/participate to benchmark):** DEF CON Quals, PlaidCTF, HITCON, Google CTF main event, corCTF, *CTF, Real World CTF.
- **How to pick:** on CTFtime, look for events with `weight` < 25 and "beginner" in the description for your first season; read last year's writeups to gauge difficulty.
- **Adjacent:** [HackerOne](https://www.hackerone.com/)/[Bugcrowd](https://www.bugcrowd.com/) CTFs & invite events (web skills transfer directly), Trace Labs Search Party (OSINT for missing persons — real impact).

## 4. Ranked Shortlists per Category

### Web Exploitation
1. **PortSwigger Academy** — structured, complete, free; non-negotiable.
2. **OverTheWire: Natas** — 33 levels of progressive web wargame.
3. **PentesterLab** — curated real-CVE badges.
4. **OWASP Juice Shop** — self-hosted intentionally-vulnerable app.
5. **HTB Web challenges / RootMe Web-Server** — volume of harder scenarios.

### Pwn / Binary Exploitation
1. **pwn.college** — the most structured path from zero to heap.
2. **Nightmare** — technique-by-technique with real CTF binaries.
3. **Exploit Education Phoenix** — bite-sized progressive VMs.
4. **ROP Emporium** — ROP-specific drills.
5. **pwnable.kr / wargames on RootMe App-System** — classic ladders.
6. **HTB Pwn challenges / pwnable.xyz** — harder, rated practice.

### Reverse Engineering
1. **crackmes.one** — infinite supply at every difficulty.
2. **pwn.college RE modules** — taught, not just given.
3. **Microcorruption** — teaches RE habits in a game loop.
4. **reversing.kr** — short and surgical.
5. **Flare-On** (annual, archived) — the RE world championship; treat early-years challenges as endgame material.

### Cryptography
1. **CryptoHack** — from base64 to lattices.
2. **Cryptopals** — implement the attacks; the de-facto standard.
3. **picoGym Crypto** — gentle volume.
4. **RootMe Cryptanalysis** — classic ciphers through RSA.
5. **MysteryTwister (MTC3)** — decades of archived cipher challenges; dated UI, excellent content.

### Forensics / Steganography
1. **picoGym Forensics** — approachable breadth.
2. **CyberDefenders** — realistic investigation scenarios.
3. **MemLabs** — memory-forensics focused scenarios.
4. **HTB Sherlocks** — DFIR narrative cases.
5. **RingZer0 stego section** — dense stego-specific volume.

### OSINT
1. **OSINT Dojo** — ranked beginner→advanced path.
2. **TryHackMe rooms: OhSINT, Sakura Room** — guided geolocation/username investigations.
3. **Bellingcat challenges** — real-world styled verification puzzles.
4. **Gralhix (Sofia Santos) exercises** — classic geolocation drills with solutions.
5. **Trace Labs events** — competitive OSINT for actual missing-persons cases.

### General / Finding Your Feet
1. **picoCTF + picoGym** → 2. **CTFlearn** → 3. **247CTF** → 4. **RootMe** → 5. **weekend CTFtime events**.

## Where Am I on the Roadmap?

This list maps to the phases in the [main README](README.md): Learning platforms carry Phase 0–1, practice pools carry Phase 1–3, and CTFtime events are the thread running through all of them.

---

_Back to the [main roadmap](README.md)_
