#!/usr/bin/env bash
#
# install-pwn.sh - CTF binary exploitation (pwn) toolchain for Kali / Debian / Ubuntu.
#
# Installs:
#   apt : gdb, gdbserver, patchelf, socat, checksec, build tools, ruby
#   pip : pwntools, ROPgadget, ropper
#   gem : one_gadget, seccomp-tools
#   git : pwndbg (as default gdb init), GEF (via gdb-gef wrapper), libc-database
#
# Usage:
#   ./install-pwn.sh          install everything
#   DRY_RUN=1 ./install-pwn.sh    print every command without changing anything
#
# Idempotent: safe to re-run; existing clones are pulled, not re-cloned.
#
set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"
TOOLS_DIR="${TOOLS_DIR:-$HOME/tools}"

# ---------------------------------------------------------------- helpers
log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

run() {
    if [ "$DRY_RUN" = "1" ]; then
        printf '  DRY>'
        printf ' %q' "$@"
        printf '\n'
    else
        "$@"
    fi
}

command -v apt-get >/dev/null || die "apt-get not found - this script targets Kali/Debian/Ubuntu."

SUDO=""
if [ "$(id -u)" -ne 0 ]; then
    if command -v sudo >/dev/null; then
        SUDO="sudo"
    elif [ "$DRY_RUN" = "1" ]; then
        warn "not root and no sudo found - continuing because DRY_RUN=1"
        SUDO="sudo"
    else
        die "not root and sudo not installed. Install sudo or run as root."
    fi
fi

# PEP 668: modern Kali/Debian marks system python as externally managed
PIP_FLAGS=()
if compgen -G "/usr/lib/python3*/EXTERNALLY-MANAGED" >/dev/null; then
    PIP_FLAGS=("--break-system-packages")
    log "Externally-managed python detected - pip will use --break-system-packages"
fi

clone_or_update() {
    local url="$1" dest="$2"
    if [ -d "$dest/.git" ]; then
        log "updating $(basename "$dest")"
        run git -C "$dest" pull --ff-only || warn "pull failed for $dest (kept existing copy)"
    else
        log "cloning $url"
        run mkdir -p "$(dirname "$dest")"
        run git clone --depth=1 "$url" "$dest"
    fi
}

install_apt() {
    log "apt: updating package index"
    run $SUDO apt-get update
    log "apt: installing $*"
    if ! run $SUDO apt-get install -y "$@"; then
        warn "bulk apt install failed - retrying package-by-package"
        local pkg
        for pkg in "$@"; do
            run $SUDO apt-get install -y "$pkg" || warn "skipped unavailable package: $pkg"
        done
    fi
}

pip_install() {
    log "pip: $*"
    run pip3 install --user "${PIP_FLAGS[@]}" --upgrade "$@"
}

# ---------------------------------------------------------------- 1. apt
install_apt \
    gdb gdbserver \
    python3 python3-pip python3-dev \
    git curl wget ca-certificates \
    build-essential patchelf file checksec unzip \
    ruby-full \
    socat netcat-openbsd

# ---------------------------------------------------------------- 2. pip
pip_install pwntools ROPgadget ropper

# ---------------------------------------------------------------- 3. gems
# (system-wide so one_gadget/seccomp-tools land on PATH for every shell)
log "gem: one_gadget, seccomp-tools"
run $SUDO gem install --no-document one_gadget seccomp-tools

# ---------------------------------------------------------------- 4. pwndbg (default gdb plugin)
clone_or_update https://github.com/pwndbg/pwndbg "$TOOLS_DIR/pwndbg"
if grep -qs pwndbg "$HOME/.gdbinit" 2>/dev/null; then
    ok "pwndbg already sourced in ~/.gdbinit"
else
    log "running pwndbg setup (installs its python deps, writes ~/.gdbinit)"
    run "$TOOLS_DIR/pwndbg/setup.sh"
fi

# ---------------------------------------------------------------- 5. GEF (side-by-side via wrapper)
# pwndbg stays the default; `gdb-gef <binary>` runs gdb with GEF instead.
clone_or_update https://github.com/hugsy/gef "$TOOLS_DIR/gef"
if [ "$DRY_RUN" = "1" ]; then
    echo "  DRY> create ~/.local/bin/gdb-gef wrapper"
else
    mkdir -p "$HOME/.local/bin"
    cat > "$HOME/.local/bin/gdb-gef" <<EOF
#!/bin/sh
# GEF alongside pwndbg: -nx skips ~/.gdbinit (which sources pwndbg)
exec gdb -q -nx -ex "source $TOOLS_DIR/gef/gef.py" "\$@"
EOF
    chmod +x "$HOME/.local/bin/gdb-gef"
fi
case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) warn "\$HOME/.local/bin is not on your PATH - add it (e.g. in ~/.zshrc) to use gdb-gef" ;;
esac

# ---------------------------------------------------------------- 6. libc-database
clone_or_update https://github.com/niklasb/libc-database "$TOOLS_DIR/libc-database"
log "libc-database installed. Populate it once (large download):"
log "    cd $TOOLS_DIR/libc-database && ./get ubuntu debian"

# ---------------------------------------------------------------- verify
log "verifying installation..."
fails=0
check() {
    if [ "$DRY_RUN" = "1" ]; then echo "  DRY> would verify: $1"; return 0; fi
    if command -v "$1" >/dev/null; then ok "$1"; else warn "MISSING: $1"; fails=$((fails+1)); fi
}
for c in gdb gdbserver python3 pip3 git checksec patchelf socat ROPgadget ropper one_gadget seccomp-tools; do
    check "$c"
done
if [ "$DRY_RUN" != "1" ]; then
    if python3 -c "import pwn" 2>/dev/null; then
        ok "pwntools importable"
    else
        warn "pwntools import failed - check pip output above"
        fails=$((fails+1))
    fi
fi
[ "$fails" -eq 0 ] && ok "pwn toolchain installed." || warn "$fails tool(s) missing - check the log above."
