# Solve: Notepad Remembers

> Full walkthrough for `challenge.md` using Volatility 3. Commands are exact and copy-pasteable; outputs below are representative (PIDs/addresses vary per dump). Hands-on data: MemLabs Lab 1 follows this exact path.

---

## Step 1 — Identify the image (the vol3 "imageinfo")

Volatility 3 has no profiles. Ask it to identify what it's looking at:

```bash
vol -f memdump.raw windows.info
```

```text
Variable                Value
Kernel Base             0xf8000264c000
DTB                     0x187000
Symbols                 file:///.../windows/symbols/ntkrnlmp.pdb/...
Is64Bit                 True
SystemTime              2023-08-14 02:55:12
NtSystemRoot            C:\Windows
```

64-bit Windows image, symbols matched. Proceed. (For a Linux dump you'd run `vol -f mem.raw banners.Banners` instead to learn the kernel version.)

## Step 2 — Process inventory: find the outlier

```bash
vol -f memdump.raw windows.pstree
```

```text
PID    PPID   ImageFileName      Offset(V)        Threads  Handles  CreateTime
...
4      0      System             0x8a1b040        97       512      02:12:44
296    4      smss.exe           ...
384    296    csrss.exe          ...
412    296    wininit.exe        ...
488    412    services.exe
556    488    svchost.exe        ...
1992   3344   explorer.exe       ...
2576   1992   notepad.exe        0x9c2e000        3        89       02:47:31
* 3676 2576  svch0st.exe        0x9d11440        4        210      02:48:02
```

Two red flags in one dump:

1. `notepad.exe` (PID 2576) — matches "just took some notes", keep in mind.
2. **`svch0st.exe` (PID 3676) with a zero instead of an o, parented by *notepad*.** A real `svchost.exe` is a child of `services.exe`. Classic masquerading + odd parent.

Also worth one command of paranoia against unlinked processes:

```bash
vol -f memdump.raw windows.psscan | grep -i svch0st
```

## Step 3 — What was it doing?

```bash
vol -f memdump.raw windows.cmdline | grep -E 'notepad|svch0st'
```

```text
2576  notepad.exe    "C:\Windows\System32\notepad.exe" C:\Users\admin\Desktop\creds.txt
3676  svch0st.exe    "C:\Users\admin\AppData\Local\Temp\svch0st.exe" -k 4444 --dump C:\Users\admin\Desktop\creds.txt
```

There it is: Notepad editing `creds.txt`, and the dropped binary reading the same file and phoning out on port 4444.

```bash
vol -f memdump.raw windows.netscan | grep 3676
```

```text
TCPv4  10.0.0.15  4444   185.220.101.4  4444   ESTABLISHED   3676   svch0st.exe
```

Outbound connection confirmed. (In the MemLabs version of this story, netscan historically shows nothing — CTF authors vary; cmdline is the reliable hit.)

## Step 4 — Dump the suspect processes and loot them

The flag is almost certainly either in notepad's memory (the text being edited) or in the dropper's. Dump both:

```bash
mkdir -p dumps
vol -f memdump.raw windows.memmap --pid 2576 --dump   # notepad
mv pid.2576.dmp dumps/notepad.dmp
vol -f memdump.raw windows.memmap --pid 3676 --dump   # dropper
mv pid.3676.dmp dumps/svch0st.dmp
```

Loot with strings (this is the step where CTF memory challenges actually fall):

```bash
strings dumps/notepad.dmp | grep -i -E 'flag\{|ctf\{'
```

```text
flag{v0lat1l1ty_psl1st_ftw}
```

If Notepad hadn't held it, the dropper dump and `malfind` are the next stops:

```bash
vol -f memdump.raw windows.malfind --pid 3676 --dump
strings dumps/svch0st.dmp | grep -i -E 'flag\{|http|password'
```

And the laziest universal fallback — memory is strings, all the way down:

```bash
strings memdump.raw | grep -i 'flag\{'
```

## Step 5 — (bonus) Pull credentials while you're here

```bash
vol -f memdump.raw windows.hashdump   # NTLM hashes — crack: hashcat -m 1000
vol -f memdump.raw windows.lsadump    # LSA secrets: sometimes plaintext domain creds
```

Not needed for this flag, but IR writeups always ask. Habit > relearning.

## Flag

```text
flag{v0lat1l1ty_psl1st_ftw}
```

## Lessons Learned

1. **`pstree` before `pslist`** — a wrong parent directory outs a masqueraded process instantly.
2. **Misspellings are confession letters:** `svch0st`, `scvhost`, `exp1orer`. Grep for them by hand; tooling won't do it for you.
3. **`memmap --dump` + `strings` is the flag factory** for notepad/browser/editor-style memory challenges.
4. The vol3 flow is fixed: `windows.info` → `pstree`/`psscan` → `cmdline` → `netscan` → dump → strings. Run it the same way every time and memory challenges stop being scary.
