# Contributing

> How to add writeups, notes, tools, and resources to this repository — naming conventions, content standards, and the definition of a "complete" note.

---

## Repository Map

Before adding content, put it in the right place:

| Where | What belongs there |
|---|---|
| `fundamentals/` | Cross-category knowledge (Linux, assembly, Python, encodings) |
| `categories/<category>/README.md` | Overview of one CTF category |
| `categories/<category>/tools.md` | Tool table + usage snippets for that category |
| `categories/<category>/cheatsheet.md` | One-page fast-reference for use during a live CTF |
| `categories/<category>/notes/` | Deeper, topic-per-file notes (e.g. `padding-oracle.md`) |
| `categories/<category>/examples/` | Worked challenge examples with full reasoning |
| `quick-ref/` | Ultra-dense reference tables (magic bytes, debugger commands) |
| `methodology/` | Meta-strategy: approach, time management, writeups |
| `environment/` | Setup guides, Dockerfiles, install scripts |
| `scripts/` | Reusable exploit/solver templates |
| `writeups/` | Full writeups from live events, one folder per event |
| `resources.md` | Curated external links (books, courses, channels) |
| `platforms.md` | Practice/learning/competition platform directory |

If content doesn't fit anywhere, open an issue first instead of creating a new top-level directory.

---

## Adding a Writeup

1. **Wait until the event ends.** Never publish solutions while a CTF is live or use flags from an active event.
2. Create a folder for the event if it doesn't exist: `writeups/<event-slug>/` e.g. `writeups/2025-picoctf/`.
3. Add your file: `writeups/<event-slug>/<challenge-slug>.md` e.g. `writeups/2025-picoctf/buffer-overflow-1.md`.
4. **Use the template:** copy `methodology/writeup-template.md` as your starting point and fill every section.
5. Images and other assets go in `writeups/<event-slug>/assets/` and are linked relatively.
6. Include your final solve script inline in a fenced code block. If the script is long, also drop it in the event folder next to the writeup.
7. Credit the challenge author/organizer and any teammates or external writeups that helped you.

## Adding Notes

1. Pick the category folder that matches the topic (`categories/crypto/notes/`), or `fundamentals/` if it's cross-category.
2. Check the table of contents of the existing files first — extend an existing note instead of creating a near-duplicate.
3. One topic per file: `padding-oracle.md`, not `crypto-everything.md`.
4. Follow the content standard below.

## File Naming Conventions

- **Markdown files:** lowercase kebab-case — `format-string-bugs.md`, `heap-basics.md`
- **Scripts:** lowercase snake_case with descriptive names — `rsa_small_e.py`, `xor_brute.py`
- **Event folders:** `<year>-<event-slug>` — `2025-google-ctf`, `2026-bsides-noida`
- **Challenge files:** the challenge name slugified — `web-cached-login.md`
- **UPPERCASE** is reserved for `README.md`, `CONTRIBUTING.md`, and Dockerfiles
- No spaces, no special characters, no version numbers in filenames (`notes-v2.md` is what git is for)

## What a Complete Note Looks Like

A note is **complete** when all of the following are true:

- [ ] Uses the standard header structure (title → one-line summary blockquote → horizontal rule → sections → footer link back to the roadmap)
- [ ] States prerequisites up front ("read `x86-assembly.md` first")
- [ ] Explains the *why*, not just the *what* — a reader should understand when to apply it
- [ ] Contains at least one **worked example** with real commands and real (sanitized) output
- [ ] All commands have actually been run and verified by the author
- [ ] Lists common pitfalls / error messages and what causes them
- [ ] Ends with 1–3 high-quality external references for going deeper
- [ ] Cross-links to related notes in the repo where relevant

A note is **incomplete** if it has placeholder text, dead links, untested commands, copy-pasted content from another site, or examples you can't reproduce. Incomplete content is still welcome as a PR — just mark it clearly:

```markdown
> Status: DRAFT — commands not yet verified independently.
```

## Content Rules

- **Write in your own words.** Quote and cite; never bulk-copy from blogs, docs, or other repos. Link the original instead.
- **Test every command** in a real environment before submitting. Docker images under `environment/docker/` exist so you can.
- **No lorem ipsum, no vague placeholders.** If a section isn't ready, cut it.
- **No emojis** in documentation (repo convention).
- Code blocks must have a language tag (` ```bash `, ` ```python `, ` ```text `).
- Keep cheat sheets dense; keep notes explanatory. Don't blur the two.

## Pull Request Process

1. Fork and branch: `add/crypto-padding-oracle-note`, `fix/install-pwn-typo`
2. Keep PRs focused: one note, one fix, or one category batch per PR
3. Commit messages: short imperative subject — `add padding oracle note`, `fix ffuf install flag`
4. In the PR description: what you added, why it belongs where it is, and how you verified it
5. Self-review with this checklist:
   - [ ] File is in the right directory and named per conventions
   - [ ] Header structure matches other files in that directory
   - [ ] Commands/scripts were executed and produce the claimed output
   - [ ] Links resolve
   - [ ] No emojis, no placeholders, no copied text

---

_Back to the [main roadmap](README.md)_
