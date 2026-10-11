#!/usr/bin/env bash
#
# install-all.sh - run every category install script in one shot.
#
# Usage:
#   ./install-all.sh                  run all available install-*.sh scripts
#   ./install-all.sh --pwn --web      run only the selected ones
#   DRY_RUN=1 ./install-all.sh        show everything without changing anything
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN="${DRY_RUN:-0}"
export DRY_RUN

log()  { printf '\033[1;34m[*]\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m[+]\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m[!]\033[0m %s\n' "$*" >&2; }
die()  { printf '\033[1;31m[x]\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
    sed -n '2,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

# ---------------------------------------------------------------- pick scripts
ALL="pwn web rev crypto"
SELECTED=""

if [ "$#" -eq 0 ]; then
    SELECTED="$ALL"
else
    for arg in "$@"; do
        case "$arg" in
            --pwn)    SELECTED="$SELECTED pwn" ;;
            --web)    SELECTED="$SELECTED web" ;;
            --rev)    SELECTED="$SELECTED rev" ;;
            --crypto) SELECTED="$SELECTED crypto" ;;
            --all)    SELECTED=" $ALL" ;;
            -h|--help) usage; exit 0 ;;
            *) die "unknown option: $arg (try --help)" ;;
        esac
    done
fi

# ---------------------------------------------------------------- run them
ran=0
skipped=0

for kind in $SELECTED; do
    script="$HERE/install-$kind.sh"
    if [ ! -f "$script" ]; then
        warn "no script for '$kind' ($script missing) - skipping"
        skipped=$((skipped+1))
        continue
    fi
    log "================ install-$kind.sh ================"
    if bash "$script"; then
        ok "install-$kind.sh finished"
    else
        warn "install-$kind.sh exited with an error - continuing with the rest"
    fi
    ran=$((ran+1))
done

echo
ok "done: $ran script(s) executed, $skipped skipped."
if [ "$DRY_RUN" = "1" ]; then
    warn "DRY_RUN=1 was set - nothing was actually changed."
fi
