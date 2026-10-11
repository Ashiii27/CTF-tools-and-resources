# Windows Forensic Artifacts

> Where Windows remembers everything: registry hives, prefetch, LNK files, jump lists, SRUM, shimcache, amcache — what each one proves and which tool parses it. This is "what did the user/attacker **do**" territory.

---

## The Big Picture

| Question | Artifact(s) |
|---|---|
| What programs ran? | Prefetch, Amcache, Shimcache, BAM/DAM |
| What files were opened? | LNK files, Jump Lists, RecentDocs (registry) |
| What was plugged in? | USBSTOR (registry), setupapi.log |
| Who logged in, from where? | Security.evtx (4624/4625), RDP bitmap cache |
| What persisted? | Run keys, services, scheduled tasks |
| What was exfiltrated? | SRUM (per-app network usage!) |
| What was deleted/how? | $MFT, $UsnJrnl, Recycle Bin (see disk-forensics.md) |

## Registry Hives

Hives are binary databases. Live locations: `C:\Windows\System32\config\` (SAM, SYSTEM, SOFTWARE, SECURITY) and per user `NTUSER.DAT` + `UsrClass.dat`. Offline, parse with **Registry Explorer**, **RECmd**, `regripper` (`rip.pl`), or `pip install regipy` on Linux.

| Hive | Good stuff inside | Example keys |
|---|---|---|
| **SAM** | Local users, RIDs, NTLM hashes | `SAM\Domains\Account\Users` (with SYSTEM hive → hashdump) |
| **SYSTEM** | Services, USB devices, shimcache, timezone | `SYSTEM\CurrentControlSet\Services`, `...\Enum\USBSTOR` (every USB ever attached + first/last seen times) |
| **SOFTWARE** | Installed programs, OS version, network profiles | `Microsoft\Windows\CurrentVersion\Uninstall` |
| **NTUSER.DAT** | Everything about *one* user: Run-key persistence, recently opened | `...\CurrentVersion\Run`, `...\Explorer\RecentDocs`, `UserAssist` (ROT13-encoded! proves program launches w/ run count + last-run time) |
| **USRCLASS.DAT** | Shellbags — folders the user **browsed** (even deleted folders) | `Local Settings\Software\Microsoft\Windows\Shell` |

Quick triage: `rip.pl -r NTUSER.DAT -p userassist` / `rip.pl -r SYSTEM -p usbstor`. Volatility can also read hives from memory (`windows.hivelist`, `windows.printkey`).

## Prefetch (`C:\Windows\Prefetch\*.pf`)

Windows caches metadata for launched executables to speed startups — which means a durable **record of execution**: `EVIL.EXE-1A3F56C9.pf` tells you the binary ran, from what path (volume info inside), how many times (Win7- era), and the last run time (Win8+: last 8 run times).

```powershell
PECmd.exe -d C:\evidence\Prefetch --csv out\     # Zimmerman
# linux quick check:
strings 'EVIL.EXE-1A3F56C9.pf' | head            # path visible in plaintext
```

Notes: prefetch happens even when say "I never ran malware" — executing from new paths stands out. Server SKUs often disable prefetch (check `SYSTEM\...\Prefetcher`).

## LNK Files (`*.lnk` — shortcuts)

Created automatically when a user opens a file (Recent, pinned, jump entries). Even after the target is deleted, the LNK proves it existed and keeps the target's **path, timestamps (target's own MAC times at open time!), volume serial, and machine MAC address**. Parse: `LECmd.exe -f file.lnk`.

CTF angle: a LNK named `flag.lnk` pointing at `C:\Users\admin\Documents\totally\real\path\flag.txt` just told you where the flag *was* — and maybe its encoding name.

## Jump Lists

`AutomaticDestinations\` and `CustomDestinations\` under `AppData\Roaming\Microsoft\Windows\Recent` — per-application MRU lists (recent docs in Notepad, recent folders in Explorer). Proof of *"this app touched these files"*. `JLECmd` parses them.

## SRUM — Network Exfil Detector

`C:\Windows\System32\sru\SRUDB.dat` (ESE database): System Resource Usage Monitor records **per-application, per-hour network bytes sent/received**, CPU, energy. An attacker can't easily scrub it.

```powershell
SrumECmd.exe -f SRUDB.dat -r SOFTWARE --csv out\   # SOFTWARE hive improves app-name resolution
```

Question answered: "which process pushed 4 GB outbound at 03:12?" — one row in SRUM. (WSL/Linux note: parse with `ESEDatabaseView` on Windows.)

## Shimcache (Application Compatibility Cache)

Lives in the **SYSTEM** hive: `SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache`. Tracks executable paths (+ last modified time, and on some versions an executed flag) for binaries that touched the compat layer — famously keeps entries even for **deleted** executables. Order roughly = execution insertion order on Win10/11.

```powershell
AppCompatCacheParser.exe -t -f SYSTEM --csv out\
```

## Amcache

`C:\Windows\AppCompat\Programs\Amcache.hve` — records executed/installed programs **with SHA1 hashes**, file paths, link times. The "did this exact binary (hash) exist here" oracle. `AmcacheParser.exe -f Amcache.hve --csv out\`.

## Event IDs for Login / Lateral Movement (the movement table)

| What happened | Events |
|---|---|
| Local console login | 4624 **Type 2** (+ 4672 if admin) |
| **RDP login** | 4624 **Type 10**; paired: TerminalServices-RdpCoreTS 131 / -RemoteConnectionManager 1149 |
| **Network share access (SMB lateral)** | 4624 **Type 3**, then 5140 (share accessed) / 5145 (file-level access attempt) |
| **Explicit creds (psexec/runas/net use)** | **4648** with the *target host* inside, often + 4624 type 3 |
| Failed sprays | 4625 bursts (0xC000006A) then one 4624 |
| Service installed (persistence, psexec) | **7045** in System log; 4697 in Security |
| Scheduled task persistence | **4698** created / 4702 updated; task content in `C:\Windows\System32\Tasks\<name>` |
| New attacker account | **4720** created → 4732 (added to Administrators) → logins as that user |
| Cleanup | **1102** Security log cleared |

Chain in a story: `4648 (admin → WS01) → 4624 type3 on WS01 → 7045 'evil-svc' → 5145 ADMIN$ write`. That's textbook lateral movement, fully evidenced.

## Offline Collection & Parsing Speedrun

- **KAPE** (Zimmerman): targets collector+parser runner; the standard way pros grab all of the above from a mounted image in minutes.
- Order for CTF: `MFTECmd` on $MFT → PECmd on Prefetch → Registry (Run keys + USBSTOR + UserAssist) → EvtxECmd the Security/System logs → SRUM if exfil's the question.

---

_Back to the [main roadmap](../../../README.md)_
