# Encoding & Decoding

> Encoding is not encryption — if it looks like a flag got "scrambled" but no key exists, it's an encoding chain. Identification guide, decode commands, and how to chain-solve.

---

## The Quick Identification Table

| Looks like | Alphabet / pattern | Encoding |
|---|---|---|
| `ZmxhZ3t9` (maybe `=`/`==` tail) | A–Z a–z 0–9 `+` `/`, `=` padding | Base64 |
| `MFRGGZDF` (uppercase + digits, `=` tail) | A–Z 2–7, `=` padding | Base32 |
| `7gstYfzjk9XpyM` | a–zA–Z0–9 but **no** `0 O I l`, no padding | Base58 (Bitcoin alphabet) |
| `666c6167` | only 0–9 a–f, even length | Hex |
| `01100110 01101100` | 0s and 1s, groups of 8 | Binary ASCII |
| `146 154 141 147` or `0x66 0x6c` | numbers 0–255 or prefixed hex | Decimal/ASCII codes |
| `%66%6C%61%67` or `flag%20here` | `%` + hex pairs | URL encoding |
| `\x66\x6c` or `\\u0066` | C-style escapes | Python/C unescape, Unicode code points |
| `SYNT{ncc}` | readable-ish words, letters shifted | ROT13/Caesar |
| `-.-. ..-. ` | dots, dashes, `/` spaces | Morse |
| `s9W3N0:W3QQ@*W38d` | dense printable ASCII, no padding | Base85/Ascii85 |
| Intel hex `:1061..`-style lines | `:` + hex records | SREC/Intel HEX (hardware challenges) |
| `BRNF{...}` nothing matches | maybe it's actually encrypted | See XOR/crypto notes |

Rule of thumb: **count the distinct characters.** ~64 → Base64; 32 uppercase → Base32; 16 → hex; 2 → binary; punctuation `%` → URL; `shift readable by a constant` → Caesar family.

## Decode Commands (No Browser Needed)

```bash
# Base64 / Base32
echo 'ZmxhZ3tiYXNlfQ==' | base64 -d
echo 'MZWGCZ33ON2A====' | base32 -d

# Hex
echo '666c6167' | xxd -r -p

# Binary → text
echo '0110011001101101' | perl -lpe '$_=pack"B*",$'

# URL encoding
python3 -c 'import urllib.parse,sys; print(urllib.parse.unquote(sys.argv[1]))' '%66%6C%61%67%7B%75%72%6C%7D'

# ROT13 (and any ROT)
echo 'SYNT{pelb}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'

# ASCII codes
python3 -c 'print("".join(map(chr,[102,108,97,103])))'
```

## Encoding Chains

Challenges apply several encodings in sequence. **Work from the outside in** — identify the outermost layer, decode, re-identify, repeat.

```text
JTdCJTdE... → (URL-decode) → aGFzaGNy... == → (b64-decode) → 5212127b... → (hex) → Rf..{...}
```

Tell-tale signs of a chain:
- A Base64 string that decodes to *another* Base64-looking string
- Hex that unhexes to something ending in `=` (that's Base64 next)
- Result is printable but not ASCII-English → it may be the ciphertext of a simple cipher (XOR/Caesar) with the key as part of the puzzle

**Decode-loop snippet** — tries the common decoders for N rounds and shows candidates:

```python
import base64, binascii, urllib.parse

def try_decoders(data: str):
    out = {}
    for name, fn in {
        "url": lambda s: urllib.parse.unquote(s),
        "b64": lambda s: base64.b64decode(s).decode("utf-8", "ignore"),
        "b32": lambda s: base64.b32decode(s).decode("utf-8", "ignore"),
        "hex": lambda s: binascii.unhexlify(s).decode("utf-8", "ignore"),
        "rot13": lambda s: __import__("codecs").decode(s, "rot_13"),
    }.items():
        try:
            r = fn(data)
            if r and r != data and all(32 <= ord(c) < 127 for c in r):
                out[name] = r
        except Exception:
            pass
    return out

s = "JTdCJTdE"
for round_ in range(5):
    print(f"--- round {round_}: {s[:60]}")
    cands = try_decoders(s)
    if not cands:
        break
    for k, v in cands.items():
        print(f"  [{k}] {v[:80]}")
    s = max(cands.values(), key=len)        # continue with the longest plausible candidate
```

Run it, eyeball each round, and stop when a flag format appears. For gnarlier combinations use [CyberChef](https://gchq.github.io/CyberChef/) "Magic" (its auto-detector) — and keep [dCode.fr](https://www.dcode.fr/en) open for classical ciphers.

## Unicode & Character-Set Traps

- **UTF-8 vs UTF-16:** every-other-byte-is-`0x00` (`f\x00l\x00a\x00g\x00` in a hexdump) = UTF-16-LE. `iconv -f UTF-16LE -t UTF-8 file`.
- **Homoglyphs:** a "flag" may use Cyrillic/Greek look-alikes (`а` U+0430 vs `a` U+0061). If a visibly-correct flag fails, check code points: `python3 -c 'print([hex(ord(c)) for c in input()])'`.
- **Zero-width characters** (U+200B, U+FEFF) hide data in "plain" text — select-all in a browser to spot them, or check `len(text)` vs visible length.
- **`\u{...}` escapes:** JavaScript `"\u0066\u006c\u0061\u0067"` decodes to `flag`.

## Identification Quick Hits

```bash
file mystery.bin          # start of every identification
file -k mystery.bin       # keep-going: reports composite types too
xxd mystery.bin | head    # eyeball magic bytes → quick-ref/magic-bytes.md
wc -c mystery.bin         # length hints (multiples of 8/16 → block cipher/crypto)
head -c 100 mystery.bin | strings   # any readable scaffolding?
```

---

**Practice:** picoCTF's "Warmup/Bases" series, then OverTheWire Krypton — encoding layers are exactly its difficulty ramp.

_Back to the [main roadmap](../README.md)_
