# Magic Bytes — File Signatures

> The bytes at the start of a file that identify it, regardless of extension. The first table of every forensics challenge.

**Inspect:** `xxd file | head -3` · **Identify:** `file file` (and `file -k` for composite types) · **Carve/hunt:** `binwalk file`

---

## Images

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| PNG | `89 50 4E 47 0D 0A 1A 0A` | `.PNG....` | Must end with `IEND AE 42 60 82`; truncation = broken render |
| JPEG | `FF D8 FF E0` / `E1` / `DB` / `EE` | `....` | E0 = JFIF, E1 = Exif (metadata lives here) |
| GIF87a / GIF89a | `47 49 46 38 37 61` / `... 39 61` | `GIF87a` `GIF89a` | 89a supports animation — check every frame |
| BMP | `42 4D` | `BM` | |
| TIFF (LE / BE) | `49 49 2A 00` / `4D 4D 00 2A` | `II*.` / `MM.*` | |
| WebP | `52 49 46 46 ?? ?? ?? ?? 57 45 42 50` | `RIFF....WEBP` | RIFF container, `WEBP` at offset 8 |
| ICO | `00 00 01 00` | | |
| PSD | `38 42 50 53` | `8BPS` | |

## Archives & Packages

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| ZIP | `50 4B 03 04` | `PK..` | `PK\x05\x06` = empty archive, `PK\x07\x08` = spanned |
| — also ZIP: | docx, xlsx, pptx, apk, jar, epub, nupkg, odt | | Office docs and APKs are ZIPs; `unzip` them |
| GZIP | `1F 8B` | | |
| BZIP2 | `42 5A 68` | `BZh` | |
| XZ | `FD 37 7A 58 5A 00` | `.7zXZ.` | |
| 7z | `37 7A BC AF 27 1C` | `7z...` | |
| RAR ≤4 | `52 61 72 21 1A 07 00` | `Rar!...` | |
| RAR 5 | `52 61 72 21 1A 07 01 00` | | |
| TAR | *(offset 257)* `75 73 74 61 72` | `ustar` | No magic at offset 0! |
| CAB | `4D 53 43 46` | `MSCF` | |
| AR (deb) | `21 3C 61 72 63 68 3E` | `!<arch>` | `.deb` files |
| RPM | `ED AB EE DB` | | |

## Executables & Bytecode

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| ELF | `7F 45 4C 46` | `.ELF` | Byte 5: 01=32-bit, 02=64-bit |
| PE (exe/dll) | `4D 5A` | `MZ` | PE header at offset in `0x3C`; string "This program cannot be run in DOS mode" nearby |
| Mach-O 32 / 64 | `FE ED FA CE` / `FE ED FA CF` | | Byte-swapped variants `CE FA ED FE` / `CF FA ED FE` |
| Fat/Universal Mach-O | `CA FE BA BE` | | Multi-arch macOS binary |
| Java class | `CA FE BA BE` | | Same magic as fat Mach-O — disambiguate with `file` |
| WASM | `00 61 73 6D` | `.asm` | WebAssembly |
| Python .pyc | version magic + `0D 0A` | | Magic number varies per Python version; decompile per version |
| SWF | `46 57 53` / `43 57 53` / `5A 57 53` | `FWS`/`CWS`/`ZWS` | C = zlib-compressed, Z = LZMA |
| DEX (Android) | `64 65 78 0A 30 33 35 00` | `dex.035.` | Or 037–040 |

## Documents & Databases

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| PDF | `25 50 44 46 2D` | `%PDF-` | Ends `%%EOF`; content streams may be compressed |
| OLE2/CFB (doc, xls, ppt, msi, msg) | `D0 CF 11 E0 A1 B1 1A E1` | | Old Office = compound file; `oletools`/`7z x` to inspect |
| SQLite3 | `53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00` | `SQLite format 3.` | `sqlite3 file .tables`; check for deleted rows |
| SQLite journal | `D9 D5 05 F9 20 A1 63 D7` | | Rollback journal = deleted data still inside |
| PEM | `2D 2D 2D 2D 2D` | `-----` | Text armor; base64 between BEGIN/END lines |
| XML | `3C 3F 78 6D 6C` | `<?xml` | Text formats often have no magic at all |

## Media & Captures

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| WAV | `52 49 46 46 ?? ?? ?? ?? 57 41 56 45` | `RIFF....WAVE` | Check spectrogram for hidden data |
| MP3 | `49 44 33` or `FF FB` / `FF F3` / `FF F2` | `ID3` | ID3 = metadata header; FF Fx = raw frame sync |
| FLAC | `66 4C 61 43` | `fLaC` | |
| OGG | `4F 67 67 53` | `OggS` | |
| MIDI | `4D 54 68 64` | `MThd` | Note data can encode messages |
| MP4/MOV | `?? ?? ?? ?? 66 74 79 70` | `ftyp` at offset 4 | Brand follows: `isom`, `mp42`, `qt  ` |
| MKV/WebM (EBML) | `1A 45 DF A3` | | |
| AVI | `RIFF....AVI ` | | |
| PCAP | `D4 C3 B2 A1` / `A1 B2 C3 D4` | | LE / BE; nanosecond variants `4D 3C B2 A1` / `A1 B2 3C 4D` |
| PCAPNG | `0A 0D 0D 0A` | | |

## Disk & VM

| Type | Hex signature | ASCII hint | Notes |
|---|---|---|---|
| ISO 9660 | `43 44 30 30 31` at offset `0x8001` | `CD001` | CD image |
| LUKS | `4C 55 4B 53 BA BE` | `LUKS..` | Encrypted volume header |
| QCOW2 | `51 46 49 FB` | `QFI.` | |
| VMDK | `4B 44 4D` | `KDM` | (sparse; descriptor files are text) |
| EnCase E01 | `45 56 46 09 0D 0A FF 00` | `EVF` | Forensic image |

## Fonts & Misc

| Type | Hex signature | ASCII hint |
|---|---|---|
| TTF | `00 01 00 00` | |
| OTF | `4F 54 54 4F` | `OTTO` |
| WOFF / WOFF2 | `77 4F 46 46` / `77 4F 46 32` | `wOFF` / `wOF2` |
| Blender | `42 4C 45 4E 44 45 52` | `BLENDER` |

---

## CTF Exploitation of Signatures

**1 -> Extension lies.** Always `file` first. A `.png` that's really a ZIP is a giveaway for a two-part challenge.

**2 -> Truncation repair.** Broken image? It may just be cut off:
- PNG: ensure it ends with `IEND AE 42 60 82`; append if missing: `printf '\x49\x45\x4e\x44\xae\x42\x60\x82' >> file.png`
- ZIP: try `zip -FF broken.zip --out fixed.zip`

**3 -> XOR-key recovery from known magic.** If a "corrupted" file is XORed with a repeating key, the first bytes leak the key:

```python
expected = bytes.fromhex("89504E470D0A1A0A")          # PNG magic
with open("mystery.bin","rb") as f: data = f.read()
key = bytes(a ^ b for a, b in zip(expected, data))     # XOR first N bytes
out  = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
open("recovered.png","wb").write(out)
```

**4 -> Carving:** `binwalk -e file`, `foremost -i file -o out/`, `scalpel file -o out/` recover embedded files by their signatures.

_Reference: [Wikipedia list of file signatures](https://en.wikipedia.org/wiki/List_of_file_signatures)_

---

_Back to the [main roadmap](../README.md)_
