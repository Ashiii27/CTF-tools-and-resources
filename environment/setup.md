# Environment Setup

> Choosing and configuring your CTF workhorse: OS distro comparison, VM vs bare metal tradeoffs, recommended VM settings, and honest WSL2 limitations.

---

## Choosing a Distro

| | Kali Linux | Parrot OS | Ubuntu/Debian |
|---|---|---|---|
| **Purpose-built for** | Offensive security | Offensive security + privacy | General use |
| **Pre-installed tools** | Almost everything (nmap, Burp, sqlmap, ghidra…) | Similar set, slightly leaner | Almost nothing — you install what you need |
| **Footprint** | Heavy | Medium | Light |
| **Stability** | Rolling release; breaks occasionally | Rolling release | Very stable (LTS) |
| **Docs/community** | Largest for pentesting topics | Good | Largest overall |
| **pip behavior** | PEP 668 externally-managed (use pipx or `--break-system-packages`) | Same | Same on recent releases |

**Recommendation:**

- New to CTF? **Kali in a VM.** Every tutorial assumes it and the answer to "how do I install X" is usually "it's already there."
- Comfortable with Linux and want a clean daily base? **Ubuntu/Debian + the install scripts in `environment/scripts/`**. You get only the tools you understand.
- Parrot is a fine Kali alternative; everything in this repo applies to it equally.

## VM vs Bare Metal vs WSL2 vs Docker

| Approach | Pros | Cons |
|---|---|---|
| **VM (VirtualBox/VMware)** | Full isolation, snapshots before risky ops, real network adapters, GPU-free tools are fine | RAM/disk overhead, clunky clipboard until guest tools are set up |
| **Bare metal / dual boot** | Full performance, real hardware access (Wi-Fi, USB RF tools) | A broken update costs you; host OS security tradeoff |
| **WSL2** | Instant launch, shares files with Windows, great for scripting | No USB passthrough without usbipd-win, no raw-socket tricks, networking is NAT'd (see below) |
| **Docker containers** | Reproducible, disposable, one per category (see `environment/docker/`) | Not a full KVM environment; needs flags for ptrace/GDB |

**Practical setup used by most regular players:** Kali VM as the main attack box, WSL2 for quick Python one-offs, and a disposable Docker container per pwn challenge so its libc matches the challenge.

## Recommended VM Settings (VirtualBox & VMware)

| Setting | Value | Why |
|---|---|---|
| RAM | 4 GB minimum, 8 GB if you run Burp/Ghidra | Ghidra decompiling Java and Burp are memory-hungry |
| vCPUs | 2 (4 if host has 8+) | Compiling + brute force is faster |
| Disk | 60–80 GB, **dynamically allocated** | Wordlists, Docker images and memory dumps grow fast |
| Virtualization | Enable VT-x/AMD-V in BIOS | Without it, 64-bit guests won't boot |
| **Guest Additions / open-vm-tools** | Install immediately | Enables the next two rows |
| Shared clipboard | Bidirectional | Copying flags in/out of the VM |
| Drag & drop | Bidirectional (verify per-file; disable during malware analysis) | Moving challenge files around |
| Network | **NAT** for most CTFs; Bridged only when the target must see you on the LAN | NAT shields your VM from the LAN and works on hostile Wi-Fi |
| Video memory | 128 MB, disable 3D acceleration if the screen goes black | Classic black-screen fix |
| Snapshots | One clean snapshot after setup, one before every event | 30-second rollback when you torch the toolchain |

**VirtualBox guest additions on Kali:** `sudo apt install virtualbox-guest-x11` then reboot.
**VMware tools on Kali:** `sudo apt install open-vm-tools-desktop` then reboot.

## WSL2 Notes and Limitations

WSL2 is an excellent scripting companion, but know the edges:

- **What works great:** Python/pwntools, GDB, Ghidra (via WSLg on Windows 11), CyberChef in browser, SSH clients, tmux.
- **Raw networking:** no easy raw sockets/promiscuous mode. `nmap` SYN scans and Wireshark capture are unreliable. Run scanners inside the Kali VM instead.
- **USB passthrough:** not native. [usbipd-win](https://github.com/dorssel/usbipd-win) can share a device (`usbipd bind`, `usbipd attach`) — works for SDR and Flipper-style hardware, with fiddling.
- **Networking is NAT'd:** your Windows host is reached via the gateway IP (`ip route | awk '/default/ {print $3}'`), not `127.0.0.1`. Listening services in WSL2 are forwarded to Windows localhost automatically, but not to the LAN by default.
- **File systems:** editing Windows files under `/mnt/c` from Linux is 5–10x slower than native ext4 (`~/`). Keep challenge files in the Linux filesystem.
- **systemd:** enable it via `/etc/wsl.conf` (`[boot]\nsystemd=true`) if a tool's installer assumes it.
- **GUI apps:** work on Windows 11 via WSLg (`sudo apt install wireshark` then `wireshark` just opens). Sound and some GL features are hit-or-miss.

## Post-Install

Whatever you chose, continue with:

1. `environment/kali-setup.md` — distro post-install steps and fixes
2. `environment/scripts/install-all.sh` — install per-category toolchains
3. `environment/docker/` — disposable per-challenge containers (optional but recommended for pwn)

---

_Back to the [main roadmap](../README.md)_
