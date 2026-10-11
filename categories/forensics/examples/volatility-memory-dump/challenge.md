# Challenge: Notepad Remembers

**Category:** Forensics — Memory
**Difficulty:** Beginner → Intermediate
**Points:** 300

---

## Story

> A junior admin's workstation started behaving strangely after they opened a
> "spreadsheet" from an email. Antivirus found nothing, but the machine was
> observed making outbound connections. Before pulling the plug, IR captured a
> full memory dump.
>
> The admin swears they "just took some notes in Notepad."
>
> Find out what process was acting up, what it was doing, and recover the flag
> the attacker was after.

## Artifacts

- `memdump.raw` — full RAM capture from the workstation (Windows)

*(Memory dumps are too large to ship in a git repo. To follow the walkthrough
with real hands-on data, download **MemLabs Lab 1** —
`https://github.com/stuxnet999/MemLabs` — which is built around exactly this
flow, or use any Windows memory sample from the
[Volatility Foundation samples list](https://github.com/volatilityfoundation/volatility/wiki/Memory-Samples).
The commands in `solve.md` are identical; only the PIDs and offsets differ.)*

## Goal

1. Identify the suspicious process (name + PID)
2. Determine what it was doing
3. Recover the flag from its memory

Format: `flag{...}`
