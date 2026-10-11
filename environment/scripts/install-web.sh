#!/usr/bin/env bash
#
# install-web.sh - CTF web exploitation toolchain for Kali / Debian / Ubuntu.
#
# Installs:
#   apt : ffuf, gobuster, sqlmap, nikto, nmap, wordlists, seclists, jq, curl
#   git : SecLists fallback (only if the apt package is unavailable)
#
# Note: Burp Suite Community is a GUI app - use the packaged download from
# https://portswigger.net/burp/communitydownload or the ready-to-run container
# in environment/docker/web.Dockerfile instead.
#
# Usage:
#   ./install-web.sh          install everything
#   DRY_RUN=1 ./install-web.sh    print every command without changing anything
#
# Idempotent: safe to re-run.
#
set -euo pipefail

DRY_RUN="${DRY_RUN:-0}"
TOOLS_DIR="${TOOLS_DIR:-$HOME/tools}"

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

# ---------------------------------------------------------------- 1. core tools
log "apt: updating package index"
run $SUDO apt-get update

PACKAGES="ffuf gobuster sqlmap nikto nmap curl wget git jq wordlists python3 python3-pip python3-requests"
log "apt: installing $PACKAGES"
if ! run $SUDO apt-get install -y $PACKAGES; then
    warn "bulk apt install failed - retrying package-by-package"
    for pkg in $PACKAGES; do
        run $SUDO apt-get install -y "$pkg" || warn "skipped unavailable package: $pkg"
    done
fi

# ---------------------------------------------------------------- 2. SecLists / wordlists
if run $SUDO apt-get install -y seclists; then
    ok "seclists installed (usually at /usr/share/seclists)"
else
    warn "no seclists apt package - cloning SecLists to $TOOLS_DIR/SecLists instead"
    clone_or_update https://github.com/danielmiessler/SecLists "$TOOLS_DIR/SecLists"
fi

# ---------------------------------------------------------------- 3. rockyou
if [ "$DRY_RUN" = "1" ]; then
    echo "  DRY> would decompress /usr/share/wordlists/rockyou.txt.gz if present"
elif [ -f /usr/share/wordlists/rockyou.txt.gz ] && [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    log "decompressing rockyou.txt"
    run $SUDO gzip -dk /usr/share/wordlists/rockyou.txt.gz
else
    ok "rockyou already available (or wordlists package missing)"
fi

# ---------------------------------------------------------------- 4. Burp note
log "Burp Suite Community is a GUI app and is intentionally NOT installed here."
log "   Download: https://portswigger.net/burp/communitydownload"
log "   Or use:   environment/docker/web.Dockerfile (jre + jar included)"

# ---------------------------------------------------------------- verify
log "verifying installation..."
fails=0
for c in ffuf gobuster sqlmap nikto nmap curl git jq python3; do
    if [ "$DRY_RUN" = "1" ]; then echo "  DRY> would verify: $c";
    elif command -v "$c" >/dev/null; then ok "$c";
    else warn "MISSING: $c"; fails=$((fails+1)); fi
done
[ "$fails" -eq 0 ] && ok "web toolchain installed." || warn "$fails tool(s) missing - check the log above."

cat <<'TIP'

 Quick test:
   ffuf -u http://example.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt
TIP
