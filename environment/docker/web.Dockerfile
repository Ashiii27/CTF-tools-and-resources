# Web exploitation environment: Burp Suite Community, ffuf, sqlmap, gobuster, nikto
#
# Build:  docker build -f web.Dockerfile -t ctf-web .
# Run (CLI tools only):
#         docker run --rm -it -v "$PWD":/work ctf-web
# Run (Burp GUI via X11 on the host):
#         xhost +local:docker
#         docker run --rm -it -e DISPLAY=$DISPLAY \
#           -v /tmp/.X11-unix:/tmp/.X11-unix -v "$PWD":/work ctf-web burp
#
# Wordlists live at /usr/share/seclists (e.g.
#   ffuf -u http://target/FUZZ -w /usr/share/seclists/Discovery/Web-Content/common.txt)
#
FROM kalilinux/kali-rolling:latest

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffuf \
        sqlmap \
        gobuster \
        nikto \
        nmap \
        seclists \
        wordlists \
        curl wget git jq \
        python3 python3-pip python3-requests \
        openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

# Burp Suite Community (portable JAR).
# Pin a version with &version=2025.x.y if reproducibility matters; without
# the parameter PortSwigger serves the latest community release.
RUN mkdir -p /opt/burp \
    && curl -fSL \
       "https://portswigger.net/burp/releases/download?product=community&type=Jar" \
       -o /opt/burp/burpsuite_community.jar \
    && java -jar /opt/burp/burpsuite_community.jar --version 2>/dev/null | head -1 || true \
    && printf '#!/bin/sh\nexec java -jar /opt/burp/burpsuite_community.jar "$@"\n' \
       > /usr/local/bin/burp \
    && chmod +x /usr/local/bin/burp

# Decompress rockyou
RUN [ -f /usr/share/wordlists/rockyou.txt.gz ] \
    && gzip -dk /usr/share/wordlists/rockyou.txt.gz || true

WORKDIR /work

# Sanity: tools respond to --help/--version
RUN ffuf -V && sqlmap --version && gobuster version && nikto -Version 2>/dev/null | head -2

CMD ["/bin/bash"]
