# Disk Forensics

> Working with disk images (`.img`/`.dd`/`.E01`): mounting them, reading partition tables, finding deleted files, and following a repeatable workflow. Assumes you know Linux but are new to forensics.

---

## First Principles

A disk image is a **byte-for-byte copy of a storage device** — boot sector, partition table, filesystems, deleted files' leftovers and all. That's the point: deleting a file removes its *directory entry*, not (immediately) its *content*. Your job is usually to find what the filesystem forgot.

```bash
# ALWAYS work on a copy, and always record the original's hash
md5sum evidence.img | tee evidence.img.md5
cp evidence.img work.img
```

## Step 1 — Understand the Layout (Partition Table)

```bash
mmls work.img
```

```text
DOS Partition Table
Offset Sector: 0
Units are in 512-byte sectors
      Slot      Start        End          Length       Description
000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
001:  -------   0000000000   0000002047   0000002048   Unallocated
002:  000:000   0000002048   0001048575   0001046528   Linux (0x83)
003:  000:001   0001048576   0002097151   0001050624   NTFS / exFAT (0x07)
```

Key facts that unlock everything else:
- Offsets are in **sectors** (usually 512 bytes). Byte offset = `start × 512`.
- `fdisk -l work.img` and `parted work.img unit s print` show the same info.
- Hidden/unallocated space between and after partitions is a classic hiding spot: `dd if=work.img bs=512 skip=2097152 count=100 | xxd | head`.

## Step 2 — Mount It (Read-Only, Always)

```bash
# method 1: mount with a byte offset (start sector × 512)
sudo mount -o ro,loop,offset=$((2048*512)) work.img /mnt/img

# method 2: let losetup create per-partition devices
sudo losetup -fP --show work.img        # → /dev/loop0, with loop0p1, loop0p2...
sudo mount -o ro /dev/loop0p1 /mnt/img
```

For `.E01` (Expert Witness) images, convert logically first with `ewfmount` (package `ewf-tools`):

```bash
sudo mkdir /mnt/ewf /mnt/img && sudo ewfmount image.E01 /mnt/ewf
sudo mount -o ro,loop /mnt/ewf/ewf1 /mnt/img    # ewf1 is the raw view
```

Cleanup: `sudo umount /mnt/img && sudo losetup -d /dev/loop0`.

## Step 3 — Work the Filesystem Without Mounting (Sleuth Kit)

Mounting changes nothing if you use `ro`, but TSK is faster, and sees deleted entries natively. All TSK tools take `-o <start sector>` to address a partition directly:

```bash
fls -o 2048 work.img                 # list root dir of partition starting at sector 2048
fls -o 2048 -r work.img              # recursive — everything
fls -o 2048 -r -d work.img           # deleted entries only — the money command
```

Deleted still-allocated entries show with `*`:

```text
r/r * 9228:    important_backup.zip
```

Recover it by **inode** with `icat`:

```bash
icat -o 2048 work.img 9228 > important_backup.zip
file important_backup.zip
```

`istat -o 2048 work.img 9228` shows an inode's full metadata — create/modify/delete times (forensics loves timestamps). Bulk-extract everything including deleted files: `tsk_recover -e work.img recovered/`.

## Step 4 — Deleted File Recovery (deeper)

If `fls -d` shows nothing but the challenge insists something was deleted:

1. **Carve the unallocated space.** Extract it and run a carver:
   ```bash
   blkls -o 2048 work.img > unallocated.bin
   foremost -i unallocated.bin -o carved/
   ```
2. **Journal/slack space.** Ext filesystems keep a journal; older file content survives in file slack. `photorec` (from testdisk) brute-carves well here.
3. **Recycle Bin / Trash.** NTFS: `$Recycle.Bin/<SID>/$I*` (index) + `$R*` (content) — the `$I` file stores the original path and deletion time. Linux: `.local/share/Trash/`.

## The NTFS Artifacts You Should Know

| Artifact | Where | What it gives you |
|---|---|---|
| `$MFT` | root of volume | Master File Table — every file that ever existed; parse with `MFTECmd` or `analyzeMFT` (`pip install analyzemft`) |
| `$LogFile` | root of volume | NTFS journal — recent create/write/delete operations |
| `$UsnJrnl:$J` | `$Extend` | Change journal — *why/when* files changed |
| `$Recycle.Bin` | per-user | Deleted files with original paths |
| `Thumbs.db` / thumbcache | Explorer folders | Proof an image was *viewed*, may hold deleted thumbnails |

On ext4 the analogous targets are the journal (`debugfs` can walk it), `lost+found`, and unallocated blocks.

## Suggested Workflow (checkpoint list)

1. `md5sum`, copy, work on the copy.
2. `mmls` / `fdisk -l` → note partitions **and unallocated gaps**.
3. Mount each partition `ro` (or live in TSK), browse normally.
4. `fls -r -d` for deleted entries → `icat` them out.
5. Check trash/recycle, then carve unallocated with foremost/photorec.
6. Timelines: `fls -m` + `mactime` builds a quick filesystem timeline without full plaso.
7. Still stuck? `bulk_extractor` the whole image and grep its URL/email/feature reports.

**Common CTF placements:** a ZIP carved from unallocated space, a flag in file slack appended after a JPEG's EOI marker, a password in a deleted `.txt`, or the second partition everyone forgets to mount.

---

_Back to the [main roadmap](../../../README.md)_
