# pwndbg Commands — The Ones You Always Forget

> Print-worthy reference for GDB + [pwndbg](https://github.com/pwndbg/pwndbg). Plain-GDB equivalents included for when you're on a box without it.

---

## Launch & Run

| Command | Does |
|---|---|
| `gdb ./chall` | load binary |
| `gdb -p <pid>` | attach to running process |
| `starti` | **break at the very first instruction** (before main — the #1 forgotten command) |
| `run < input.txt` | run with file as stdin |
| `set args A B C` | set argv for future `run`s |
| `attach <pid>` / `detach` | attach/detach |
| `set follow-fork-mode child` | debug the child after a `fork()` (server challenges) |
| `delete` | delete all breakpoints |

## Breakpoints & Stepping

| Command | Does |
|---|---|
| `b main` | break at function |
| `b *0x401234` | break at **address** (don't forget the `*`) |
| `b *main+67` | break at function offset |
| `tbreak` / `delete` / `disable 1` / `enable 1` | temporary / remove / toggle breakpoints |
| `info breakpoints` | list |
| `ni` / `si` | next/step **instruction** (ni skips into calls) |
| `next` / `step` | source-line versions |
| `finish` | run until current function returns |
| `c` | continue |
| `until *0x401240` | run until an address |

## Reading State

| Command | Does |
|---|---|
| `context` | repaint the pwndbg dashboard (regs/disasm/stack) |
| `regs` | pwndbg register view |
| `telescope $rsp 30` | **dereferenced chain view of stack memory** — the pwndbg superpower |
| `x/20gx $rsp` | classic: 20 giant (8-byte) hex words (LE notation) |
| `x/32bx $rsp` | bytes |
| `x/s $rsi` | C string at address |
| `x/10i $rip` | disassemble instructions |
| `vmmap` | **memory map with permissions** — find stack/heap/libc bases (GDB: `info proc mappings`) |
| `search -t string "flag"` | search all of memory for a string |
| `search -p $rsp` | search memory for a pointer |
| `dump binary memory out.bin 0xSTART 0xEND` | write a memory range to a file |
| `p/x $rax` | print register as hex |
| `info functions` / `info variables` | symbols |
| `procinfo` | pwndbg process summary |

## Binary Analysis (in-debugger)

| Command | Does |
|---|---|
| `checksec` | protections of the loaded binary |
| `got` / `plt` | show GOT/PLT tables with resolved addresses |
| `elfheader` | ELF headers |
| `piebase` | where the PIE binary actually loaded — add offsets from static analysis to this |
| `breakrva 0x1234` | break at PIE-relative offset (the piebase-math killer feature) |
| `aslr` / `aslr off` (`set disable-randomization on`) | toggle ASLR for debugging |
| `rop --grep "pop rdi"` | pwndbg's built-in gadget search |
| `nearpc` | short disassembly around $rip |
| `patch *0x401234 "nop"` | assemble & write a patch into memory |

## Heap

| Command | Does |
|---|---|
| `vis` | **visualized heap chunks** (`vis_heap_chunks`) — learn to love it |
| `heap` | chunks of an arena |
| `bins` / `tcache` / `fastbins` / `unsortedbin` | view each bin |
| `arena` | show current arena |
| `malloc_chunk 0xADDR` | describe a chunk header |
| `find_fake_fast 0xADDR` | find fake fastbin targets |
| `try_free 0xADDR` | dry-run a free to see glibc's complaint |
| `set resolve-heap-via-heuristic Force` | when heap analysis trusts symbols the target doesn't have |

## Patterns & Utilities

| Command | Does |
|---|---|
| `cyclic 200` | De Bruijn pattern (same as `pwn cyclic` on the CLI) |
| `cyclic -l 0x6161616c` | **offset of a value** — find your exact RIP offset from a crash |
| `canary` | print the current stack canary |
| `distance 0xA 0xB` | byte distance between two addresses (buffer→ret-addr math) |
| `set context-sections "regs disasm code stack backtrace"` | slim down the dashboard |
| `theme` / `config` | pwndbg settings |
| `python <code>` | run Python with GDB's API from the prompt |
| `source script.py` | load a pwndbg/python script |

## One-Liners Outside GDB

```bash
pwn checksec ./chall                 # protections without starting gdb
pwn cyclic 200                       # pattern
pwn cyclic -l 0x6161616c             # offset lookup
pwn template ./chall > solve.py      # pwntools template generator
gdb -batch -ex 'b main' -ex run -ex 'x/20gx $rsp' ./chall   # scripted session
```

## Migrating from PEDA / GEF

| PEDA | pwndbg |
|---|---|
| `pattern_create 200` | `cyclic 200` |
| `pattern_offset` | `cyclic -l <value>` |
| `checksec` | `checksec` |
| `vmmap` | `vmmap` |
| `telescope` | `telescope` |
| `searchmem "str"` | `search "str"` |
| `context` | `context` |
| `xuntil` | `until <addr>` |

Running both pwndbg and GEF on the same system: keep **one** sourced in `~/.gdbinit`, launch the other with `gdb -q -nx -ex "source /path/to/gef.py"` (see `environment/scripts/install-pwn.sh` for the `gdb-gef` wrapper).

---

_Back to the [main roadmap](../README.md)_
