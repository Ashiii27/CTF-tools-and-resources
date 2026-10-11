# Python for CTF

> Python is the default CTF language. This note covers the five libraries that solve 90% of challenges: bytes handling, `struct`, pwntools, requests, and PyCryptodome — plus the ctypes escape hatch.

---

## Setup

```bash
pip3 install --user pwntools pycryptodome requests
# On modern Kali/Debian, if pip refuses (PEP 668), use:
pip3 install --user --break-system-packages pwntools pycryptodome requests
```

See `environment/kali-setup.md` for the externally-managed details.

## Bytes vs str — the #1 Source of CTF Bugs

Python 3 separates text (`str`) and data (`bytes`). Almost every "my script doesn't work" bug is a mix-up between them.

```python
b"A" == "A"                      # False — never equal
s = "flag{abc}"
b = s.encode()                   # str → bytes
s2 = b.decode()                  # bytes → str

b[0]                             # 102 (an int, not a 1-char byte string!)
chr(102), ord(b"f")              # 'f', 102

b.hex()                          # '666c6167...'
bytes.fromhex("666c6167")        # b'flag'
hex(0xdead)                      # '0xdead'

# int ↔ bytes with explicit byte order (crypto challenges live on this)
(0x1337).to_bytes(2, "big")      # b'\x13\x37'
int.from_bytes(b"\x13\x37", "big")   # 0x1337

# Byte-order helpers (same thing, crypto-flavored)
from Crypto.Util.number import long_to_bytes, bytes_to_long
long_to_bytes(0x666c6167)        # b'flag'

# XOR — write this helper once, use it forever
def xor(data: bytes, key: bytes) -> bytes:
    return bytes(d ^ key[i % len(key)] for i, d in enumerate(data))
```

## struct — Pack/Unpack Raw Binary

For building payloads and parsing binary protocols. Format characters (prefix `<` = little-endian, `>` = big-endian):

| Char | C type | Size |
|---|---|---|
| `B` | uint8 | 1 |
| `H` | uint16 | 2 |
| `I` | uint32 | 4 |
| `Q` | uint64 | 8 |
| `x` | pad byte | 1 |

```python
import struct
struct.pack("<I", 0xdeadbeef)      # b'\xef\xbe\xad\xde'
struct.unpack("<Q", b"A"*8)[0]     # 0x4141414141414141
```

**In practice, use pwntools instead** — `p32`/`p64`/`u32`/`u64` do the same with fewer imports and correct endianness from `context.binary`:

```python
from pwn import p64, u64
p64(0xdeadbeef)                    # b'\xef\xbe\xad\xde\x00\x00\x00\x00'
u64(b"\xef\xbe\xad\xde\x00\x00\x00\x00")   # 0xdeadbeef
```

## pwntools Basics

```python
from pwn import *

context.log_level = "debug"        # see every byte on the wire (drop to "info" once it works)

# --- talking to things ---
io = remote("host.ctf.local", 1337)    # TCP service
io = process("./chall")                # local binary

io.recvline()                          # one line (with \n)
io.recvuntil(b"name: ")                # read until a marker
io.sendline(b"admin")                  # write line
io.sendafter(b"pass: ", b"x"*32)       # recvuntil + send in one call
io.clean()                             # drain whatever is buffered
io.interactive()                       # hand the keyboard to you (post-exploit shell)
```

**Static analysis without opening a disassembler:**

```python
elf = ELF("./chall", checksec=False)
elf.symbols["win"]                # address of the win() function
elf.got["puts"], elf.plt["puts"]  # GOT/PLT entries
elf.checksec()                    # shows NX/PIE/Canary/RELRO (also: `pwn checksec ./chall`)

p = cyclic(200)                   # 'aaaabaaacaaa...' — send as input
offset = cyclic_find(0x6161616c)  # find it again in a crash → exact RIP offset
```

**Minimal ret2win skeleton** (full version: `scripts/pwn-template.py`):

```python
payload = flat({ cyclic_find(0x6161616c): elf.symbols["win"] })
io.sendlineafter(b"> ", payload)
io.interactive()
```

Attaching the debugger mid-run: `gdb.attach(io, gdbscript="b main\nc")`.

## requests — Web Exploitation

```python
import requests

s = requests.Session()                       # keeps cookies between calls
s.headers["User-Agent"] = "ctf-solver"

# Route through Burp for inspection (toggle with env var or CLI flag)
s.proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
s.verify = False                             # needed with Burp's self-signed CA
import urllib3; urllib3.disable_warnings()   # silence the InsecureRequestWarning spam

r = s.get("http://target/api/user", params={"id": "1 OR 1=1"})
r = s.post("http://target/login", data={"u": "admin", "p": "' OR 1=1-- -"})
r = s.post("http://target/api", json={"role": "admin"})

r.status_code, len(r.content)                # boolean-blind oracle signals
r.text                                       # decoded body (str)
r.json()                                     # parsed JSON
r.cookies.get("session")
r.elapsed.total_seconds()                    # time-based blind signal
```

Full boilerplate with CLI flags and a flag-regex finder: `scripts/web-template.py`.

## PyCryptodome Essentials

```python
from Crypto.Cipher import AES
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse, GCD
from Crypto.Util.Padding import pad, unpad

# AES
cipher = AES.new(key, AES.MODE_ECB)
ct = cipher.encrypt(pad(b"attack at dawn", 16))
pt = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(ct), 16)

# RSA math (n, e, d arithmetic is just Python ints — PyCryptodome is for the utils)
p, q                    # factors of n
n = p * q
phi = (p - 1) * (q - 1)
e = 65537
d = inverse(e, phi)     # modular inverse — the line that solves half of beginner RSA
m = pow(c, d, n)        # decrypt
flag = long_to_bytes(m)
```

## ctypes — Call Shared Libraries Directly

When a challenge's RNG is a libc function, don't reimplement it:

```python
import ctypes, time
libc = ctypes.CDLL("libc.so.6")
libc.srand(int(time.time()))        # seed like the server did
libc.rand() % 256                   # predict the same stream
```

Gotcha: set `fun.restype`/`fun.argtypes` for anything that isn't an int (e.g. `libc.strlen.restype = ctypes.c_size_t`), or 64-bit pointers get truncated.

## Misc Power-Ups

```python
# Argument parsing every solver should have (see scripts/pwn-template.py)
import argparse

# Timing oracles
import time; t0 = time.perf_counter()

# Concurrent brute force
from concurrent.futures import ThreadPoolExecutor

# Talk to anything interactive the hard way (when pwntools is overkill)
import socket
```

---

**Practice:** solve a `nc`-based math quiz with pwntools, a login bypass with requests, and a small-e RSA with the `inverse()` line above — that's three categories in one afternoon.

_Back to the [main roadmap](../README.md)_
