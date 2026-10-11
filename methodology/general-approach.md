# General Challenge Approach

> What to do in the first ten minutes of any challenge, how to figure out what a challenge really is, and when to walk away and come back.

---

## The First 10 Minutes (Any Challenge)

1. **Read the description twice.** Challenge authors hide real hints in throwaway words ("*shadows* of the past", "*spinning* the wheel"). Puns are rarely accidental.
2. **Record the metadata in your notes:** event, challenge name, category, points, current solve-count, and the stated flag format.
   - More points / few solves → expect real work.
   - Many solves but it *seems* hard → you're probably missing something simple; re-read the description.
3. **Inventory the attachments.** Download everything, then triage:

   ```bash
   cd ~/ctf/events/<event>/<challenge>
   file *            # what did we actually get?
   ls -la            # hidden files, sizes
   strings -n 6 * | head -50
   binwalk *         # embedded content?
   ```
4. **Write down one sentence: "I win when..."** (e.g. *"...I read `/flag` on the server"*). Vague goals waste hours.
5. **Do a 5-minute naive attempt.** Try the obvious thing — common passwords, `strings`, default creds, the trick the description is winking at. Easy points fall here.
6. **If a service is involved, fingerprint it** before theorycrafting: headers, banners, status codes, error messages.

### Identifying the True Category

Categories lie; files don't. Quick mapping of artifact → work:

| You got | It really is | First moves |
|---|---|---|
| `.pcap` / `.pcapng` | Forensics (network) | Wireshark: statistics → protocol hierarchy, follow TCP streams, export objects |
| Binary + `libc.so.6` + remote `nc` | Pwn | `checksec`, decompile, ret2win/ret2libc thinking |
| Binary alone, asks for a "key"/"password" | Reverse engineering | Ghidra, find the check function |
| `n=... e=... c=...` or a PEM file | Crypto (RSA) | FactorDB the modulus, check common-modulus/low-e |
| Image/audio with "nothing inside" | Steganography | `exiftool`, `binwalk`, `zsteg`, spectrogram |
| Login form | Web 90% of the time | Burp, try `' OR 1=1-- -`, look at every header |
| Weird huge text file | Misc/programming | Script it; nobody parses 10k lines by hand |
| Just an IP/URL, black box | Web or boot2root | `nmap`, directory fuzz with ffuf |
| "Find where this photo was taken" | OSINT | EXIF first, then reverse image + maps |

## Working a Challenge

- **Form hypotheses explicitly.** Write "Theory: the IDOR is in `/api/order/<id>`" before testing it. Tested-and-wrong is progress; tested-and-forgotten is not.
- **Change one variable at a time** so you know which change produced the breakthrough.
- **Log payloads and outputs as you go** (your notes file doubles as your writeup draft).
- **Google is the skill:** search the error message verbatim in quotes; search `"<technology>" exploit cheat sheet`; check HackTricks/PayloadsAllTheThings for the technique you're staring at.
- **Reproduce locally when possible.** If there's a binary, run it; if it's a web app with source, spin it up in Docker. Debugging beats guessing.
- **Automate early.** If you've typed the same request three times, it belongs in `scripts/web-template.py`.

## When to Move On

Playing hard challenges is a time-allocation game. Rules of thumb:

1. **The 30–45 minute rule:** if you've made zero measurable progress for 30–45 minutes (no new information, no eliminated hypothesis), switch. Set a literal timer.
2. **Park correctly before switching:** write down (a) what you tried, (b) what you were about to try, (c) your best current theory. Future-you resumes in 2 minutes instead of 30.
3. **Revisit triggers:** a new solve by another team, a hint from organizers, or a teammate's fresh eyes are all signals to look again.
4. **Beware sunk cost.** "I've spent 3 hours on this 200-pointer" is a reason to switch *faster*, not slower.
5. **Sleep beats staring.** In 24–48h events, the overnight breakthrough is real; fatigue is the actual boss fight.

## Board Strategy (Start of an Event)

1. Spend the first 20–30 minutes **reconning the whole board**, not solving: eyeball every challenge, tag each as *easy-win / comfort-zone / stretch / skip*.
2. Grab the easy wins first — momentum and early points.
3. Assign comfort-zone challenges to teammates by category strength.
4. Keep one shared notes doc (or repo) where every parked challenge has its hypotheses listed — that's how a team avoids duplicated work.
5. Check newly-released challenges fast; early challenges are often tuned easier, and first solves boost morale (and sometimes score more under dynamic scoring).

## After the Event

- Read the top teams' writeups for everything you didn't solve, and re-solve them yourself.
- Write your writeups within 48 hours while the reasoning is fresh (`methodology/writeup-template.md`).
- Add every new trick to the matching `categories/<category>/notes/` file in this repo.

---

_Back to the [main roadmap](../README.md)_
