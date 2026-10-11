# Kali Post-Install

> The steps to run right after installing Kali, fixes for the problems everyone hits, and a battle-tested alias set.

---

## First 15 Minutes

```bash
# 1. Full upgrade (grab a coffee, this takes a while)
sudo apt update && sudo apt full-upgrade -y

# 2. Change the default password if this is a long-lived box
#    (fresh Kali images ship with kali:kali)
passwd

# 3. Timezone, keyboard, hostname
sudo dpkg-reconfigure tzdata
sudo dpkg-reconfigure keyboard-configuration
sudo hostnamectl set-hostname ctfbox

# 4. Guest tools for your hypervisor (pick one), then reboot
sudo apt install -y virtualbox-guest-x11        # VirtualBox
sudo apt install -y open-vm-tools-desktop       # VMware

# 5. Everyday quality-of-life packages
sudo apt install -y tmux htop tree jq curl wget git \
     python3-pip python3-venv pipx golang-go \
     wordlists seclists locate

# 6. Refresh the filename index (makes `locate rockyou` instant)
sudo updatedb

# 7. Decompress the most-used password wordlist
sudo gzip -dk /usr/share/wordlists/rockyou.txt.gz
```

## Directory Convention

Keep challenge files out of your home dir root — future-you will thank you:

```bash
mkdir -p ~/ctf/{events,tools,wordlists,scratch}
```

`~/ctf/events/<event>/<challenge>/` per challenge, `~/ctf/tools/` for git clones (the install scripts use this layout too), `~/ctf/scratch/` for throwaway experiments.

## pip on Modern Kali (important)

Kali's Python is *externally managed* (PEP 668) — a bare `pip3 install` fails with `externally-managed-environment`. Options in order of preference:

```bash
pipx install <pkg>                              # for CLI tools (clean, isolated)
pip3 install --user --break-system-packages <pkg>   # for libraries you must have
python3 -m venv ~/venv && source ~/venv/bin/activate  # for projects
```

The repo install scripts detect this automatically.

## Common Fixes

| Symptom | Cause / Fix |
|---|---|
| `Unable to locate package X` | `sudo apt update` first; then check `/etc/apt/sources.list` has `kali-rolling main contrib non-free non-free-firmware` |
| `Hash Sum mismatch` / GPG errors | `sudo rm -rf /var/lib/apt/lists/* && sudo apt clean && sudo apt update` |
| TLS/certificate errors on every https site | VM clock is wrong: `sudo timedatectl set-ntp true` |
| Black screen after enabling 3D acceleration | Disable 3D accel in VM settings, or `export LIBGL_ALWAYS_SOFTWARE=1` |
| VM has no network on hotel/campus Wi-Fi | Switch adapter from Bridged to NAT (Bridged breaks on captive portals) |
| Shared clipboard not working | Reinstall guest additions (above), then log out/in; verify the VM setting is *Bidirectional* |
| `pip install` → `externally-managed-environment` | See previous section |
| Docker: `Got permission denied ... /var/run/docker.sock` | `sudo usermod -aG docker $USER` then log out/in |
| GDB: `ptrace: Operation not permitted` in Docker | Run container with `--cap-add=SYS_PTRACE --security-opt seccomp=unconfined` |

## Useful Aliases

Append to `~/.zshrc` (Kali default) and/or `~/.bashrc`:

```bash
# ---- navigation / inspection ----
alias ll='ls -lah --color=auto'
alias ..='cd ..'
alias ports='ss -tulpn'                      # listening ports
alias myip='curl -s ifconfig.me; echo'       # public IP
alias genaliases='alias | sort'              # dump all aliases

# ---- CTF ergonomics ----
alias serve='python3 -m http.server 8000'    # host files for a target/box
alias listen='nc -lvnp 4444'                 # standard reverse-shell listener
alias ff='ffuf -u FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt'
alias rockyou='/usr/share/wordlists/rockyou.txt'
alias pwninit='echo "activating pwn env"; source ~/venv/bin/activate 2>/dev/null'
alias xclip='xclip -selection clipboard'     # pipe anything to clipboard: cat flag | xclip

# extract any archive without thinking
extract() {
  case "$1" in
    *.tar.gz|*.tgz)  tar xzf "$1" ;;
    *.tar.bz2|*.tbz2) tar xjf "$1" ;;
    *.tar.xz)        tar xJf "$1" ;;
    *.zip)           unzip "$1" ;;
    *.gz)            gunzip -k "$1" ;;
    *.7z)            7z x "$1" ;;
    *.rar)           unrar x "$1" ;;
    *)               echo "don't know how to extract: $1" ;;
  esac
}
```

Reload with `source ~/.zshrc`.

## Optional but Recommended

- **tmux config:** mouse mode and sane splits — `printf 'set -g mouse on\n' >> ~/.tmux.conf`
- **zsh theme:** Kali ships zsh; `sudo apt install zsh-syntax-highlighting` and add `source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh` to `~/.zshrc`
- **Git identity:** `git config --global user.name "you" && git config --global user.email "you@example.com"`
- **Snapshot now.** A clean, configured VM is worth one.

---

_Back to the [main roadmap](../README.md)_
