# Log Analysis

> Reading Windows Event Logs (`.evtx`) and Linux `auth.log`/`syslog`/web logs like an investigator: the event IDs that matter, the patterns that matter, and grep/awk recipes to find the story fast.

---

## Windows Event Logs

### Where they live and how to read them

Logs are binary `.evtx` files under `C:\Windows\System32\winevt\Logs\`. Offline (the CTF case — you're handed the files), use:

- **Event Viewer → Open Saved Log** (Windows GUI)
- **chainsaw** — `./chainsaw search Security.evtx -q 'EventID: 4625'` and `./chainsaw hunt <logdir> -s sigma/`
- **hayabusa** — `./hayabusa csv-timeline -d <logdir> -o timeline.csv` (Sigma rules built in; the fastest "what happened here" button)
- **EvtxECmd** (Zimmerman) to dump to CSV, then it's just `awk`
- **python-evtx** (`pip install evtx`) to script your own parser

### The Event IDs That Matter

**Authentication & movement:**

| Event ID | Meaning | What an investigator asks |
|---|---|---|
| **4624** | Logon success | Which *Logon Type*? 2 = console, **3 = network (SMB/psexec/wmi lateral movement)**, 7 = unlock, 8 = network cleartext (IIS basic), **10 = RDP**, 11 = cached |
| **4625** | Logon failure | Substatus code: `0xC000006A` = wrong password, `0xC0000064` = no such user. Hundreds followed by one 4624 = password sprayed/guessed |
| **4648** | Explicit credentials (`runas`, net use) | Who used whose creds, from which host — lateral movement fingerprint |
| **4672** | Special privileges at logon | Admin-tier logon; watch non-admin accounts getting it |
| **4768** | Kerberos TGT requested | Domain auth timeline |
| **4771 / 4776** | Kerberos pre-auth failed / NTLM credential validation | Brute-force indicators (`0x18` bad password) |

**Execution & persistence:**

| Event ID | Meaning |
|---|---|
| **4688** | Process created (only shows the command line if "Include command line" auditing was on — check first) |
| **4698 / 4702** | Scheduled task **created** / updated — persistence |
| **4720 / 4722 / 4726** | User account **created** / enabled / deleted — attacker account lifecycle |
| **4732** | Added to security-enabled local group (e.g. Administrators) |
| **4740** | Account lockout |
| **7045** (System log) | **New service installed** — the classic persistence find; service name + binary path right in the event |
| **1102** (Security log) | **Audit log cleared** — by itself almost a confession; everything right before it matters |
| **5156/5158** (Security) | Windows Filtering Platform connection allowed — host-level "netflow" |

**Sysmon** (if present — treat it as a superpower): `1` process create (+cmdline+hash), `3` network connect, `7` image/DLL load, `11` file created, `12/13/14` registry operations, `22` DNS query, `23` file deleted, `26` file-delete logged.

### Hunting Pattern for a .evtx Challenge

1. `hayabusa csv-timeline -d logs/ -o out.csv` → sort by level/time; Sigma hits name the attack for you.
2. No hayabusa? Extract with EvtxECmd, then pivot on **time window → user → host**:
   - When did bad stuff start? First `4625` cluster or the `1102` clear.
   - Who? The account in the suspicious `4624` type 3/10.
   - What did they do? `4688` and `7045` events for that user in that window.
3. Report: initial access → user → actions → persistence. Writeups love this chain.

---

## Linux Logs

### Where things are

```text
/var/log/auth.log     # debian/ubuntu: ssh, sudo, auth    (/var/log/secure on RHEL-ish)
/var/log/syslog       # general system chatter             (/var/log/messages on RHEL-ish)
/var/log/cron.log     # cron executions
/var/log/apache2/access.log  /var/log/nginx/access.log     # web requests
/var/log/vsftpd.log   # ftp transfers
journalctl            # systemd systems (binary journal, not grep-able directly)
```

### auth.log — the attacker's footprint

```bash
# brute force: failed logins, counted per source IP
grep -E 'Failed password' /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn

# who actually got in (and how: password vs publickey)
grep 'Accepted' /var/log/auth.log

# account manipulation
grep -E 'useradd|new user|userdel' /var/log/auth.log /var/log/syslog

# privilege use: see every sudo command
grep -E 'sudo:.*COMMAND' /var/log/auth.log

# root shells
grep 'session opened for user root' /var/log/auth.log
```

A spray-and-succeed story in three lines: 300 `Failed password` from 192.0.2.9 → `Accepted password for backup` from 192.0.2.9 → `sudo: backup : COMMAND=/bin/bash`.

### Web access.log — find the probe, then the shell

```bash
# top clients
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head

# scanner/scanner-useragents (your first clue who)
grep -iE '(sqlmap|nikto|nmap|hydra|gobuster|dirbuster|feroxbuster)' access.log

# attack strings in requests
grep -iE '(union%20select|union\+select|\.\./|%2e%2e|\{\{|<script|/etc/passwd)' access.log

# successful hits on shell-ish paths (status field $9 == 200)
awk '$9==200 {print $7}' access.log | grep -iE 'shell|cmd|upload|webshell|\.php\?'

# reconstruct one IP's whole visit in order
grep '192\.0\.2\.9' access.log | awk '{print $4, $6, $7, $9}'
```

Apache combined format fields: `$1` IP · `$4` time · `$6` method+`$7` path · `$9` status · `$10` bytes.

### Cron and services

```bash
grep -i cron /var/log/syslog | grep -ivE 'CMD \(.*(logrotate|apt|man-db)'    # unusual cron jobs
journalctl -u ssh --since '2025-03-01'    # systemd equivalent of the above grinds
```

## General Tips

- **Always build the timeline first.** Attackers assume you won't correlate; one `sort` by timestamp turns noise into a story.
- **Normalize timezones before correlating** across machines (`date`, or reformat with awk).
- **Grep for the absence too:** a gap in logs, a `1102`, or a log that *stops* mid-incident is evidence someone hid something.
- Keep a per-CTF `notes.md` of "time — host — user — event" rows. That's your writeup skeleton.

---

_Back to the [main roadmap](../../../README.md)_
