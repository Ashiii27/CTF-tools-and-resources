# Pwn environment: pwntools + GDB + pwndbg + GEF + one_gadget + libc-database
#
# Build:  docker build -f pwn.Dockerfile -t ctf-pwn .
# Run:    docker run --rm -it \
#           --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
#           -v "$PWD":/chal ctf-pwn
#
# The SYS_PTRACE/seccomp flags are required for GDB to debug inside a container.
#
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=Etc/UTC \
    LANG=C.UTF-8

# Base toolchain + debugging + ruby (for one_gadget / seccomp-tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-pip python3-dev python3-venv \
        gdb gdbserver \
        git curl wget ca-certificates \
        build-essential patchelf file checksec unzip \
        ruby-full \
        socat netcat-openbsd \
        libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Python pwn libraries
RUN pip3 install --no-cache-dir pwntools ROPgadget ropper

# pwndbg - installed as the default GDB init
RUN git clone --depth=1 https://github.com/pwndbg/pwndbg /opt/pwndbg \
    && cd /opt/pwndbg && ./setup.sh

# GEF - installed alongside (sourcing both in ~/.gdbinit conflicts);
# use the `gdb-gef` wrapper which starts GDB with GEF instead of pwndbg.
RUN git clone --depth=1 https://github.com/hugsy/gef /opt/gef \
    && printf '#!/bin/sh\nexec gdb -q -nx -ex "source /opt/gef/gef.py" "$@"\n' \
       > /usr/local/bin/gdb-gef \
    && chmod +x /usr/local/bin/gdb-gef

# one_gadget + seccomp-tools
RUN gem install --no-document one_gadget seccomp-tools

# libc-database tools. The database itself is large; fetch on first use:
#   cd /opt/libc-database && ./get ubuntu debian
# Quick usage without the full DB: https://libc.rip/ for online symbol search.
RUN git clone --depth=1 https://github.com/niklasb/libc-database /opt/libc-database
ENV PATH="/opt/libc-database:${PATH}"

WORKDIR /chal

# Version sanity check at build time
RUN python3 -c "import pwn; print('pwntools OK:', pwn.__version__)" \
    && gdb --version | head -1 \
    && test -f /opt/pwndbg/gdbinit.py && echo "pwndbg OK" \
    && test -f /opt/gef/gef.py && echo "GEF OK" \
    && one_gadget --version >/dev/null 2>&1 || true

CMD ["/bin/bash"]
