# Challenge: Data Snatchers

**Category:** Forensics — Network
**Difficulty:** Beginner
**Points:** 150

---

## Story

> The SOC flagged unusual outbound traffic from a workstation at 03:12 AM.
> We pulled 30 seconds of traffic from the mirror port and took the machine
> offline. The user insists they "only browsed the company intranet."
>
> We don't believe them. Work out what was transferred and recover whatever
> secret left the building.

## Artifacts

- `capture.pcap` — 30 seconds of mirror-port traffic

*(This repo ships a generator instead of the binary: run `python3 make_sample.py`
to produce `capture.pcap` locally. Real CTF challenges hand you the finished file.)*

## Goal

Find the flag in the transferred data. Format: `flag{...}`

## Hints

- Biggest conversation first. Size matters when data walks out the door.
- Wireshark's `File → Export Objects` is not cheating — it's the intended tool.

---

## Files in this example

| File | Purpose |
|---|---|
| `challenge.md` | this description |
| `solve.md` | full walkthrough (tshark + python), step by step |
| `solve.py` | automated solution — extracts HTTP objects and hunts the flag |
| `make_sample.py` | generates the sample `capture.pcap` used by the walkthrough |
