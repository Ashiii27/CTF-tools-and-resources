# Memory Forensics with Volatility 3

> The complete Volatility 3 workflow: identifying an image, hunting processes, dumping memory, and the exact order to run plugins in when you know nothing. Note: **Volatility 3 does not use `-profile` or `imageinfo`** — those are Volatility 2 concepts you'll see in old writeups; vol3 detects the OS automatically.

---

## Setup

```bash
pip3 install --user --break-system-packages volatility3
vol -h | head -30                       # sanity check
```

Volatility 3 downloads OS **symbol tables** from Microsoft/Linux sources on first use (needs internet). Working offline? Grab symbol packs from the [Volatility Foundation symbols page](https://downloads.volatilityfoundation.org/volatility3/symbols/) and unzip them into `volatility3/symbols/`.

## The "imageinfo Equivalent"

Old tutorials say `volatility imageinfo`. In vol3 for Windows images the equivalent (and *identification*) step is:

```bash
vol -f memory.dmp windows.info
```

It prints the detected Windows version, build, number of CPUs, and the symbol table it matched. For Linux/mac images, `banners.Banners` lists kernel banner strings it found, which identify the OS so you can pick the right symbol pack.

## How to Approach an Unknown Dump (the workflow)

Run these in order. Each stage narrows where you dig:

**1. Who was running?**

```bash
vol -f memory.dmp windows.pslist        # processes at capture time
vol -f memory.dmp windows.pstree        # parent/child tree
vol -f memory.dmp windows.psscan        # includes unlinked (rootkit-hidden) processes
```

What to flag: misspellings (`svch0st.exe`, `scvhost.exe`), system processes with wrong parents (a real `svchost.exe` is a child of `services.exe` — one spawned by `winword.exe` is malware), odd paths, and anything the story (challenge description) says the user ran. `psscan - pslist` differences are instant suspects.

**2. What did they run / type?**

```bash
vol -f memory.dmp windows.cmdline       # full command line per process — often the answer outright
vol -f memory.dmp windows.cmdline | grep -i -E 'flag|pass|\.py|\.ps1'
vol -f memory.dmp windows.envars --pid 1337
```

**3. Who were they talking to?**

```bash
vol -f memory.dmp windows.netscan       # connections + listeners + owning PID (Win7+)
```

Cross-reference suspicious PIDs from step 1. Beaconing to odd ports, or `cmd.exe` with a live connection, is your smoking gun.

**4. What files were touched?**

```bash
vol -f memory.dmp windows.filescan > filescan.txt
grep -i -E 'flag|secret|\.zip|\.kdbx' filescan.txt
```

`filescan` maps physical addresses to files the kernel knew about. Recover a file's contents straight from memory:

```bash
vol -f memory.dmp windows.dumpfiles.DumpFiles --physaddr 0x8a1b2c3d
# or everything cached for a process:
vol -f memory.dmp windows.dumpfiles --pid 1337
```

**5. Injections and hidden code:**

```bash
vol -f memory.dmp windows.malfind --dump        # RWX/hidden executable VAD regions → dumps them
```

`malfind` finds classic process-injection artifacts. The dumped regions are then `strings`-able for URLs, shellcode strings, flags.

**6. Dump the suspect process and loot it:**

```bash
vol -f memory.dmp windows.memmap --pid 1337 --dump   # full memory of pid 1337 → pid.1337.dmp
strings pid.1337.dmp | grep -i -E 'flag\{|ctf\{|password|http'
```

Notepad, browsers, and password managers routinely hold plaintext secrets; this is the single most productive move in CTF memory challenges.

**7. Registry and credentials:**

```bash
vol -f memory.dmp windows.hivelist
vol -f memory.dmp windows.printkey --key "Microsoft\Windows\CurrentVersion\Run"
vol -f memory.dmp windows.hashdump        # local NTLM hashes (crack with hashcat -m 1000)
vol -f memory.dmp windows.lsadump         # LSA secrets — sometimes plaintext creds
```

**8. The universal fallback** (works on ANY dump, any OS):

```bash
strings memory.dmp | grep -i -E 'flag\{|ctf\{|htb\{' 
```

It's crude, it's slow on multi-GB dumps, and it has won more CTF points than any plugin.

## Windows Plugin Reference

| Plugin | Shows you |
|---|---|
| `windows.info` | OS/build identification |
| `windows.pslist` / `pstree` / `psscan` | processes; tree view; unlinked ones |
| `windows.cmdline` / `envars` | command lines; environment variables |
| `windows.getsids` | which user owned each process |
| `windows.netscan` / `netstat` | sockets + owning PID |
| `windows.filescan` / `dumpfiles` | mapped files; carve them out |
| `windows.malfind` | injected/executable hidden regions |
| `windows.memmap --dump` | raw per-process memory |
| `windows.dlllist` / `handles` | loaded DLLs; open handles |
| `windows.hivelist` / `printkey` | registry hives; key contents |
| `windows.hashdump` / `lsadump` / `cachedump` | credentials |
| `windows.sessions` / `svcscan` | logon sessions; services |

## Linux / macOS Dumps

Plugin names are namespaced the same way: `linux.pslist.PsList`, `linux.pstree.PsTree`, `linux.lsof.Lsof`, `linux.envars.Envars`, `mac.pslist.PsList`… Two you will use constantly on Linux dumps:

```bash
vol -f mem.raw linux.bash.Bash > bash_history.txt   # recovered shell history — CTF gold
vol -f mem.raw linux.envars.Envars | grep -i flag
```

## A Full CTF Memory Challenge, Compressed

```bash
vol -f mem.dmp windows.info 2>&1 | head           # 1: what OS is this?
vol -f mem.dmp windows.pstree > pstree.txt        # 2: process tree → spot the odd one
vol -f mem.dmp windows.cmdline | grep -iB2 -A2 notepad   # 3: odd process context
vol -f mem.dmp windows.netscan | grep ESTABLISHED # 4: who's talking out?
vol -f mem.dmp windows.memmap --pid 1337 --dump   # 5: dump suspect
strings pid.1337.dmp | grep -i 'flag{'            # 6: loot it
```

Practice dumps: [MemLabs](https://github.com/stuxnet999/MemLabs) (six graduated labs written exactly around this workflow) and the [Volatility Foundation memory samples](https://github.com/volatilityfoundation/volatility/wiki/Memory-Samples).

---

_Back to the [main roadmap](../../../README.md)_
