# Linux for CTF

> The Linux skills that actually come up in challenges: permissions, processes, the commands you'll use hourly, piping/redirection, and bash tricks worth memorizing.

---

## File Permissions

Every file has three permission triads: **owner / group / others**, each `rwx` (read=4, write=2, execute=1).

```bash
chmod 755 script.sh      # rwxr-xr-x  (owner full, others read+exec)
chmod 644 notes.txt      # rw-r--r--
chmod +x script.sh       # symbolic form: add execute
chmod u+x,g-w file       # per-class modifications
chown user:group file    # change ownership (sudo for other users)
```

**Special bits — these are challenge material, not trivia:**

| Bit | Octal | Meaning | CTF relevance |
|---|---|---|---|
| SUID | `4xxx` | Runs with the *owner's* privileges | Privilege escalation: a SUID binary owned by root is your path in |
| SGID | `2xxx` | Runs with the *group's* privileges | Same idea, group-level |
| Sticky | `1xxx` | In a dir: only the owner can delete entries | `su` challenges, `/tmp` behavior |

```bash
find / -perm -4000 -type f 2>/dev/null    # all SUID binaries (core privesc recon)
find / -writable -type f 2>/dev/null      # files you can write to
getcap -r / 2>/dev/null                   # capabilities: SUID-like powers without SUID
```

## Process Management

```bash
ps aux | grep python            # find a process
pgrep -af ssh                   # PID + full command line
htop                            # interactive task manager
kill 1337                       # polite SIGTERM
kill -9 1337                    # SIGKILL, last resort
kill -STOP 1337                 # freeze a process (resume with -CONT)
lsof -i :4444                   # who holds port 4444?
lsof -p 1337                    # every file a process has open
/proc/1337/maps                 # its memory map (handy before gdb)
/proc/1337/cmdline              # how it was launched
```

**Job control (in a live shell):**

```text
command &        run in background
Ctrl-Z           suspend foreground job
jobs             list suspended/background jobs
bg %1            resume job 1 in background
fg %1            bring job 1 to foreground
disown %1        detach it from the shell entirely
```

CTF case: launch `nc -lvnp 4444 &`, run your exploit which connects back, `fg` into the listener to interact.

## The Commands You'll Use Hourly

| Command | Classic CTF usage |
|---|---|
| `file chall` | What is this actually? (trust it more than the extension) |
| `strings chall \| grep -i flag` | Low-hanging fruit, always first |
| `grep -rniE 'flag\{' .` | Hunt a flag pattern recursively, case-insensitive |
| `find . -size +10M` / `-newer X` / `-perm` | Locate odd files on a box |
| `xxd file \| head` | Hex-dump the first bytes (see `quick-ref/magic-bytes.md`) |
| `watch -n1 'ss -tnp'` | Poll something that changes |
| `timeout 5 ./suspicious-binary` | Run it, but not forever |
| `base64 -d payload.txt` | Decode (see `fundamentals/encoding-decoding.md`) |
| `sort a \| uniq -c \| sort -rn` | Frequency analysis |
| `diff <(sort a) <(sort b)` | Compare command outputs directly |
| `curl -sL url -o file` | Download quietly, follow redirects |
| `tar xzf a.tgz` / `unzip` / `gzip -dk` | Extract everything |
| `stat file` | Timestamps (mtime/atime/ctime) — forensics gold |
| `readlink -f link` | Resolve symlinks |
| `tr 'A-Za-z' 'N-ZA-Mn-za-m'` | ROT13 in one line |

**Text surgery trio (learn in this order):** `cut`, `awk`, `sed`.

```bash
grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' log | sort -u        # unique IPs from a log
awk '{print $1, $NF}' access.log | sort | uniq -c | sort -rn   # most-hit endpoints
sed -i 's/localhost/remote.host/g' config.txt                  # in-place replace
cut -d: -f1 /etc/passwd | sort                                 # all users on a box
```

## Piping & Redirection

```bash
cmd > out.txt        # stdout to file (overwrite)
cmd >> out.txt       # stdout to file (append)
cmd 2> err.txt       # stderr to file
cmd 2>&1 | less      # merge stderr into stdout, then pipe
cmd &> all.txt       # bash shortcut for both streams
cmd </dev/null       # starve stdin
cmd <<< "input"      # here-string: feed a string to stdin
cmd1 | tee out.txt | cmd2    # pipe AND save a copy
```

**Process substitution** — the trick beginners don't know they need:

```bash
diff <(python gen_a.py) <(python gen_b.py)   # diff two live outputs
nc target 31337 < <(python -c 'print("A"*500)')  # pipe generated input to a service
```

**Chaining:**

```text
cmd1 && cmd2     run cmd2 only if cmd1 succeeded
cmd1 || cmd2     run cmd2 only if cmd1 failed
cmd1 ; cmd2      run both regardless
```

## Bash Tricks That Save Minutes in a CTF

```bash
# Brace expansion
mkdir -p ~/ctf/events/{2023,2024,2025}/{web,pwn,crypto}
cp chall{,.backup}                    # → cp chall chall.backup

# Ranges and loops over targets
for port in {1..100}; do (echo >/dev/tcp/10.0.0.5/$port) 2>/dev/null && echo "$port open"; done
for u in $(cat users.txt); do ./try_login "$u"; done

# Command substitution
echo "flag is at $(grep -rl 'flag{' ./challenges/)"

# History
!!                  # repeat last command
sudo !!             # repeat last command as root (the classic)
!grep               # repeat last command starting with 'grep'
Ctrl-R              # reverse-search your history — the single best productivity key

# Globbing
cat **/*.txt        # recursive (needs: shopt -s globstar)
rm !(keep).txt      # delete all except keep.txt (needs: shopt -s extglob)

# Move data over thin shells
base64 bigfile | xclip                          # copy out when you can't scp
python3 -m http.server 8000                     # serve the CWD

# Find the flag-shaped thing anywhere on a compromised box
grep -rnoE '(flag|CTF|HTB)\{[^}]*\}' /home /tmp /opt 2>/dev/null
```

## Reading a Restricted Shell

Dropped into a weird shell in a challenge? Probe it:

```bash
echo $PATH; echo $0             # what's allowed / what shell is this
compgen -c | sort -u | head     # list available commands
ls -la ~/../                    # peek outside the cell
/bin/sh -i                      # try a plain interactive shell
```

---

**Further reading:** [OverTheWire: Bandit](https://overthewire.org/wargames/bandit/) (the practical companion to everything above), [explainshell.com](https://explainshell.com/) for decoding any command you copy-paste.

_Back to the [main roadmap](../README.md)_
