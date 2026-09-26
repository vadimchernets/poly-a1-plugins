# Security

## What Safecall touches

- It reads files you point Claude Code at, and copies the ones about to be changed.
- Copies go to `~/.safecall/` on your own machine. Nothing leaves the computer: there is no
  network call anywhere in this plugin, and no dependency that could make one.
- The only files it writes outside `~/.safecall/` are the ones Claude Code was already going to
  write — Safecall does not write your documents, it copies them first.

## Deliberate refusals

- **Files whose name mentions a secret are never copied.** `.env`, anything matching
  `secret`, `password`, `credential`, `token`, `id_rsa`, `id_ed25519`, `.pem`, `.key`, `.p12`,
  `.keystore`, `.netrc`, `.htpasswd`. A copy of a secret is a second secret, in a folder that is
  not guarded the way the original may be.
- **Symbolic links are not followed or copied.** A link is not the file.
- **Size limits are hard:** 5 MB a file, 50 MB a copy. A plugin that fills the disk of somebody who
  is not watching it is worse than no plugin.
- **Copies expire:** 14 days, or 20 copies per folder, whichever comes first.

## The guard hook

`scripts/guard.py` runs before `Write`, `Edit`, `MultiEdit` and `NotebookEdit`. It blocks only when
**all** of these are true: the file already exists, no copy of it was made in the last two hours,
and it has not been mentioned before. It never blocks reading, never blocks creating a new file,
and never blocks twice for the same file. If anything about the check itself fails — python
missing, timeout, unreadable input — it allows the write. **A guard must not be the thing that
breaks your session.**

## Reporting a problem

Write to polyhelper.ai@gmail.com with `safecall` in the subject. For something you would rather
not post publicly, say so in the issue without the details and a private channel will be arranged.
