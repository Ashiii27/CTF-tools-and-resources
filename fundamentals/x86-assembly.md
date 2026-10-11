# x86-64 Assembly for CTF

> Enough assembly to read disassembly, understand a stack frame, and follow a debugger — focused on x86-64 Linux, with 32-bit notes where CTFs still differ.

---

## Registers

x86-64 has 16 general-purpose registers. The low parts of each register have names too — you'll see all of them in disassembly:

| 64-bit | 32-bit | 16-bit | 8-bit (low) | Conventional role |
|---|---|---|---|---|
| `rax` | `eax` | `ax` | `al` | Accumulator; **return value** of functions; syscall number |
| `rbx` | `ebx` | `bx` | `bl` | Base; callee-saved |
| `rcx` | `ecx` | `cx` | `cl` | Counter; 4th function argument |
| `rdx` | `edx` | `dx` | `dl` | Data; 3rd function argument |
| `rsi` | `esi` | `si` | `sil` | Source index; 2nd function argument |
| `rdi` | `edi` | `di` | `dil` | Destination index; **1st function argument** |
| `rbp` | `ebp` | `bp` | `bpl` | Base pointer (frame pointer) |
| `rsp` | `esp` | `sp` | `spl` | Stack pointer — top of stack |
| `r8`–`r15` | `r8d`… | `r8w`… | `r8b`… | Extra; `r8`,`r9` are arguments 5–6 |

Special: `rip` (instruction pointer — the address of the *next* instruction; controlling this = controlling execution), `eflags` (status flags: ZF, CF, SF, OF…).

## Calling Conventions (System V AMD64 — Linux/macOS)

- **Arguments:** `rdi, rsi, rdx, rcx, r8, r9`, then stack
- **Return value:** `rax`
- **Callee-saved** (a function must preserve them): `rbx, rbp, r12–r15`
- **Caller-saved** (assume any `call` clobbers them): everything else
- The stack grows **down** (towards lower addresses) and `call` pushes a return address

*32-bit (i386):* arguments on the **stack**, return in `eax`, syscalls via `int 0x80`.
*Windows x64:* args `rcx, rdx, r8, r9` — worth a line so decompiled Windows crackmes don't confuse you.

## Common Instructions

| Instruction | Meaning | Notes |
|---|---|---|
| `mov dst, src` | copy | `mov rax, [rbx]` dereferences; `mov [rbx], rax` writes |
| `lea rax, [rbp-0x20]` | compute address, don't dereference | Also used for cheap arithmetic: `lea rax, [rdi+rdi*4]` |
| `push` / `pop` | stack ops | `push x` = `sub rsp,8; mov [rsp],x` |
| `add` / `sub` / `inc` / `dec` | arithmetic | `sub rsp, 0x40` reserves 64 bytes of locals |
| `xor eax, eax` | zero a register | Idiomatic — shorter encoding than `mov eax, 0` |
| `imul`, `mul`, `div`, `idiv` | multiply/divide | `div` uses `rdx:rax` as dividend |
| `shl` / `shr` / `sar` | shifts | `shl rax, 3` = multiply by 8 |
| `cmp a, b` then `jcc` | compare → conditional jump | Sets flags; see jump table below |
| `test a, a` then `jz` | common "is it zero/NULL" idiom | `test` = AND without storing |
| `jmp` / `call` / `ret` | control flow | `call` pushes return address; `ret` pops it into `rip` |
| `nop` | do nothing | `0x90`; patching a check to NOPs is crackme 101 |
| `leave` | `mov rsp,rbp; pop rbp` | Function epilogue |
| `syscall` / `int 0x80` | ask the kernel | x64 / 32-bit respectively |
| `cdq` / `cqo` | sign-extend into `edx/rdx` | Usually right before `idiv` |

**Conditional jumps (after `cmp`/`test`):** `je/jz` equal/zero · `jne/jnz` · `jl/jnge` (signed <) · `jg` (signed >) · `jle/jge` · `jb` (unsigned <) · `ja` (unsigned >). Signed-vs-unsigned matters for logic bugs.

## Intel vs AT&T Syntax

You'll meet both. `objdump -d` defaults to AT&T; always use `-M intel`.

| | Intel (GDB/NASM-ish) | AT&T (objdump default) |
|---|---|---|
| Operand order | `mov rax, rbx` (dst, src) | `movq %rbx, %rax` (src, dst) |
| Registers | `rax` | `%rax` |
| Immediates | `0x10` | `$0x10` |
| Memory | `[rbp-0x8]` | `-0x8(%rbp)` |
| Deref size | `QWORD PTR [rax]` | suffix `q` on mnemonic |

## The Stack Frame

```text
high addresses
┌─────────────────────┐
│   caller's locals   │
├─────────────────────┤
│   function args     │   (if more than registers)
├─────────────────────┤ ← rbp + 8
│   return address    │   ← pushed by call
├─────────────────────┤ ← rbp       (after push rbp; mov rbp, rsp)
│   saved rbp         │
├─────────────────────┤ ← rbp - 8
│   stack canary      │   (if enabled: mov rax, fs:0x28)
│   local variables   │   ← overflow target lives here
│   ...               │
└─────────────────────┘ ← rsp
low addresses
```

**Overflow sketch:** a `gets(buffer)` where `buffer` is a local lets you write past it → overwrite the canary (if present) → saved `rbp` → saved return address → you control `rip` when the function returns. (See `categories/pwn/` when it exists; the *idea* is what matters here.)

## Syscalls You'll Hardcode in Shellcode

| # (x64) | Name | Args (# / x86-32: `int 0x80`, # in `eax`) |
|---|---|---|
| 0 | read | fd=rdi, buf=rsi, n=rdx (x86: 3) |
| 1 | write | fd, buf, n (x86: 4) |
| 2 | open | path, flags (x86: 5) |
| 59 | execve | path, argv, envp (x86: 11) |
| 60 | exit | code (x86: 1) |

## Reading Disassembly: a Worked Micro-Example

```bash
objdump -d -M intel chall | sed -n '/<main>:/,/ret/p'
```

```asm
0000000000001139 <main>:
    1139:  push   rbp                    ; prologue: save frame
    113a:  mov    rbp, rsp
    113d:  sub    rsp, 0x20              ; 32 bytes of locals
    1141:  mov    rax, QWORD PTR fs:0x28 ; load stack canary...
    114a:  mov    QWORD PTR [rbp-0x8], rax  ; ...store it top of locals
    114e:  lea    rdi, [rip+0xeaf]       ; arg: "Enter password:"
    1155:  call   1030 <puts@plt>        ; puts(...)
    115a:  lea    rax, [rbp-0x30]        ; buffer = local, 0x30-0x8 = 40 bytes below canary
    115e:  mov    rdi, rax               ; arg0 = buffer
    1161:  call   1040 <gets@plt>        ; gets(buffer)  ← unbounded, overflow!
    1166:  mov    eax, 0x0               ; return 0
    116b:  mov    rdx, QWORD PTR [rbp-0x8]  ; epilogue: verify canary
    116f:  sub    rdx, QWORD PTR fs:0x28
    1178:  je     117f <main+0x46>
    117a:  call   1020 <__stack_chk_fail@plt>
    117f:  leave
    1180:  ret
```

Five CTF takeaways you can extract in seconds:

1. `<gets@plt>` — unbounded input → buffer overflow confirmed.
2. `fs:0x28` canary present → naive `rip` overwrite will be detected (`__stack_chk_fail`); you must leak the canary or hit a different target.
3. Buffer at `rbp-0x30`, canary at `rbp-0x8` → 0x28 (40) bytes of padding to the canary.
4. `call ...@plt` tells you the binary's libc surface (puts, gets) — think ret2libc.
5. `lea rdi, [rip+...]` before a call — that's a string argument; double-click it in Ghidra/IDA to read the prompt.

**C → assembly pattern cheat sheet:**

| You see | It usually was |
|---|---|
| Jump table `jmp QWORD PTR [rip+rax*8]` | `switch` statement |
| `test eax,eax; jne` around a block | `if (x)` / early return |
| Increment + compare + jump-back | `for` loop |
| A chain of `cmp je` | `if/else if/else` |
| `rep movs` / `rep stos` | `memcpy` / `memset` inlined |

---

**Further reading:** [felixcloutier.com/x86](https://www.felixcloutier.com/x86/) (every instruction), [x64 syscall table](https://x64.syscall.sh/), then practice on [crackmes.one](https://crackmes.one/).

_Back to the [main roadmap](../README.md)_
