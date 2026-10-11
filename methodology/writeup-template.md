# Writeup Template

> Copy this file's template block into `writeups/<year>-<event>/<challenge-slug>.md` and fill it in. A good writeup lets a stranger reproduce your solve without watching you do it.

---

## Rules of the House

- **Never publish before the event ends.** Check the rules; some organizers ban writeups until scoring closes.
- Fill the metadata table completely — future readers (and future you) need context.
- Include your **working** final script. Dead ends belong in "Approach", not in the solve script.
- Screenshots go in `writeups/<event-slug>/assets/` and are linked relatively.
- Credit the challenge author and anyone whose idea you built on.

## Template

````markdown
# <Challenge Name> — <Event Name> (<Year>)

| | |
|---|---|
| **Event** | <event name> |
| **Challenge** | <challenge name> |
| **Category** | web / pwn / rev / crypto / forensics / stego / osint / misc |
| **Points** | <points> |
| **Solves** | <solve count at end of event> |
| **Author** | <challenge author, if known> |
| **Writeup by** | <your handle> |
| **Flag** | `<flag{...}>` |

## TL;DR

<One-two sentences: what the bug was and the key insight. Enough that a reader
decides if this writeup is relevant to them.>

## Recon

<What we were given: files, link, service. What initial enumeration showed:
file types, open ports, technologies, interesting strings. Include commands.>

```bash
$ file chall
chall: ELF 64-bit LSB pie executable, x86-64, ...
```

## Analysis

<The reasoning: what you found digging deeper — the vulnerable function, the
weak crypto construction, the hidden stream. Include the crucial code snippet
or disassembly excerpt and annotate it.>

## Approach

<The plan you formed, attempts made — INCLUDING dead ends and why they failed.
Dead ends are the most educational part of a writeup.>

## Solution

<Step-by-step working solve, in order, reproducible end to end.>

## Solve Script

```python
# final working exploit / solver
from pwn import *
...
```

## Flag

```text
flag{the_actual_flag}
```

## Lessons Learned

<The transferable takeaway: what technique does this challenge teach, what tool
did you add to your toolbox, what would you check first next time?>

## References

- <link to related technique / original advisory / helpful writeup>
````

## Concrete Example (see it filled in)

See `writeups/` for real examples. When adding the first writeup to the repo,
follow the template literally — consistency is what makes the folder useful as
study material.

## Quality Bar (from CONTRIBUTING.md)

A writeup is complete when someone with **your skills minus this challenge's trick** can reproduce the flag using only your document and public tools. Test that claim by re-running your own solve script from scratch before publishing.

---

_Back to the [main roadmap](../README.md)_
