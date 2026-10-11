# File Carving & Format Tricks

> Pulling files out of blobs — foremost, scalpel, binwalk, manual `xxd`+`dd` carving — plus the ZIP/PNG/PDF format tricks that run every "the flag is in this file" challenge.

---

## How Carving Works

Files are usually stored **contiguously** in images/dumps. Every format announces itself with a **header** (magic bytes) and most have a **footer**. Carvers scan raw bytes for `header ... footer` pairs and cut them out, no filesystem needed. Limit: fragmented files carve corrupted — good CTF challenges avoid that; sloppy reality doesn't.

```bash
# step 0, always:
file blob.bin && xxd blob.bin | head -20 && binwalk blob.bin
```

## foremost

```bash
foremost -i blob.bin -o out/ -v             # carve everything known
foremost -t zip,png,pdf,jpg -i blob.bin -o out/   # selected types only
foremost -T -i blob.bin                     # -T: timestamped output dir
foremost -c my.conf -i blob.bin             # custom signatures
```

Custom signature lines go into a conf (see `/etc/foremost.conf` for format): `png  y  350000  \x89\x50\x4e\x47  \x49\x45\x4e\x44\xae\x42\x60\x82` (extension · case-sensitive · max size · header · footer). Output includes `audit.txt` telling you exactly what was found at which offset.

## scalpel

Faster, but config-driven — and `/etc/scalpel/scalpel.conf` **ships with every signature commented out**. Before your first run:

```bash
sudo sed -i 's/^#\(  \(jpg\|png\|gif\|zip\|pdf\|doc\)\b\)/\1/' /etc/scalpel/scalpel.conf
grep -v '^#\|^$' /etc/scalpel/scalpel.conf | head     # confirm what's enabled
scalpel blob.bin -o scalpel_out/
```

## binwalk (the first and last word)

```bash
binwalk blob.bin            # signature scan with offsets — READ these: "gzip at 0x1337"
binwalk -e blob.bin         # extract what it found
binwalk -Me blob.bin        # extract recursively (nested archives/matryoshka blobs)
binwalk -E blob.bin         # entropy plot: high-entropy island inside = compressed/encrypted blob
binwalk --dd='png image:png' blob.bin   # raw-dump matches of a chosen type
binwalk -A blob.bin         # opcode scan (find code blobs)
```

The **offset output is the real treasure**: `binwalk` prints decimal offsets you can feed straight into `dd`.

## Manual Carving (when tools shrug)

Find the offset yourself, cut it yourself:

```bash
# where's the ZIP inside this thing?
xxd blob.bin | grep -i '504b0304'        # PK\x03\x04 offsets
xxd blob.bin | grep -i '8950'            # PNG

# carve from that offset to EOF
dd if=blob.bin of=carved.zip bs=1 skip=13337 status=progress

# or with python (better for header→footer ranges)
python3 - <<'EOF'
d = open("blob.bin","rb").read()
s = d.find(b'\x89PNG\r\n\x1a\n')           # header
e = d.find(b'IEND\xaeB`\x82', s) + 8        # footer + its own length
open("carved.png","wb").write(d[s:e])
print(f"carved {e-s} bytes")
EOF
```

(`bs=1` dd is slow for big offsets — fine for CTF sizes; heavy work: `dd if=... of=... iflag=skip_bytes skip=...`.)

## Format-Specific Tricks That Are Always in CTFs

### ZIP

- **Junk before/after the ZIP.** Readers scan for the central directory, so `secret.zip` glued onto `innocent.png` opens as an image and as an archive: `unzip innocent.png` or carve from `PK\x03\x04`. WinRAR/7z care even less about prefixes.
- **Truncated archive:** `zip -FF broken.zip --out fixed.zip` rebuilds the central directory from local file headers.
- **"Password-protected" but carved by foremost?** Carvers ignore encryption flags; the entries came with the cut — though contents stay encrypted if truly enc'd (attack with `zip2john` + john, or `fcrackzip`).
- **Central directory says different things than local headers** — compare: `unzip -v` vs `zipdetails`.Flags lying about encryption = the "just extract it" trick.

### PNG

- **Data after IEND is invisible** to viewers: `xxd img.png | tail` looking for bytes after `IEND AE 42 60 82`. Truncated images fix the reverse way — append the 12-byte IEND.
- **Chunk surgery:** PNG is a chunk list (`length, type, data, CRC`). Extra flag text hides in `tEXt`/`zTXt`/`iTXt` or unknown custom chunks: `pngcheck -v img.png` lists every chunk; carve/reassembly with python.
- **Wrong dimensions:** IHDR height shrunk = picture looks small but pixel data for the full image is present. Patch height in IHDR (offset 16-19), fix the CRC (or just `pngcheck` will tell you it's wrong but viewers render anyway), re-open: the hidden band (often the flag in text) appears.

### PDF

- **Incremental updates never delete.** Text "removed" by an update is still in an earlier revision: `strings doc.pdf | grep flag`, or `qpdf --qdf --object-streams=disable doc.pdf out.pdf` then scroll the old objects.
- **Streams are (Flate) compressed:** `python3 -c "import zlib;..."` per stream, or Didier Stevens' `pdf-parser.py` — also great for suspicious `/OpenAction` JS (malware docs).
- **Embedded files:** `pdfdetach -list doc.pdf` (poppler-utils) + `pdfdetach -saveall doc.pdf`.

### JPEG

- Data after `FF D9` (EOI) is ignored by viewers — classic appendix spot.
- EXIF thumbnail inside can be a *different image* than the main one: `exiftool -b -ThumbnailImage img.jpg > thumb.jpg`.

### Office Documents

- Modern (docx/xlsx) = ZIP: `unzip doc.docx`, then hunt `word/media/`, `word/document.xml`, comments, headers.
- Legacy (doc/xls) = OLE compound: `7z x file.doc` lists streams; `oletools` (`pip install oletools`): `olevba` for macros, `oleobj` for embedded objects.

## Stego Checkpoint

If you carved out a clean image/audio with nothing visible in it — you've graduated to the stego category: `zsteg` (PNG/BMP LSB), `steghide info/extract` (JPEG/BMP), spectrogram-view the audio (Audacity/Sonic Visualiser). Carving finds the container; stego is inside the container.

---

_Back to the [main roadmap](../../../README.md)_
