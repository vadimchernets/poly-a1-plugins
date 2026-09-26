# Safecall

**Nothing is written before a copy exists. Nothing is read before you have seen the list. No answer
ends without saying what nobody checked.**

A plugin for [Claude Code](https://claude.com/claude-code), written for the person who is not a
programmer, has a folder of their own documents, and has two reasons not to let an AI near it:

1. *what if it deletes my files*
2. *what if it says something confident and wrong, and I act on it*

Safecall answers both, and adds the three readings such a person actually needs from a document.

## What it does

| | |
|---|---|
| `/safecall:before` | Lists the folder and waits before reading it. Copies every file it is about to change. |
| `/safecall:undo` | Puts the files back the way they were. The undo is itself undoable. |
| `/safecall:show` | Says what will change **before** it changes, in meaning, not in diff lines. Says where things landed after. |
| `/safecall:receipt` | Three lines under an answer: checked · **not** checked · source. |
| `/safecall:traps` | Where the catch is in a contract, loan, policy or estimate — every point with a quote. |
| `/safecall:holes` | What a plan is missing, as three questions, not thirty. |
| `/safecall:facts` | What here can be checked, what is opinion, what says nothing at all. |
| `/safecall:where` | Picks up where the last evening stopped; writes down where this one stopped. |
| `/safecall:clearer` | Turns "ну это, с банком" into a question that can be answered - by guessing two or three versions out loud, not by interrogating. |
| `/safecall:send` | Reads a letter, complaint or reply the way a cold stranger would, **before** it goes: what should not leave, blanks nobody filled in, a tone that will cost them. |
| `/safecall:named` | Checks that every file an answer names really exists on the disk, before naming it — and finds the one that is real but a folder further down. |
| `/safecall:doctor` | Why the AI is silent, in words, with one step at a time. |

Two hooks, both quiet:

- **on session start** — the real date and time of this computer (a model otherwise wishes you good
  night at ten in the morning), and where you stopped last time;
- **before writing to a file that already exists** — the guard **makes the copy itself** and lets
  the write through. Nobody is stopped: a copy costs nothing, so there is nothing to refuse. A new
  file is untouched, reading is untouched. The one refusal is a file that *cannot* be copied (its
  name mentions a password or a key) — then the change would be one-way, and the person is asked.
  With no `python3` on the machine the hooks quietly do nothing and the session works.

## Install

```
/plugin marketplace add vadimchernets/safecall
/plugin install safecall@safecall
```

Then, in `/plugin` → Marketplaces, **turn on auto-update** — for marketplaces that are not
Anthropic's own it is off by default, and without it you stay on the version you installed.

## Where the copies live

`~/.safecall/copies/`, outside your own folder, with a note in it saying not to delete it.
The name is ASCII on purpose: a folder called `снимки` cannot be typed by somebody on a Spanish
keyboard when support tells them to open it.
A copy sitting next to your documents gets mistaken for clutter and thrown away by the very person
it protects. Copies older than 14 days remove themselves; at most 20 are kept per folder; nothing
larger than 5 MB a file or 50 MB a copy.

**Files whose name mentions a password or a key are never copied** — a copy of a secret is a second
secret, and this folder is not guarded the way the original may be.

## What it never does — and the one thing it cannot promise

**Safecall itself** makes no network call, has no account, no key, and installs no second program.
Every file it writes is on your own disk and you can open all of it. Python 3.8+ and nothing else.

**But Safecall does not make Claude Code private, and this plugin will not pretend otherwise.**
A document you give Claude Code is sent to Anthropic to be read — that is how Claude Code works,
with or without this plugin. Safecall decides *whether a file can be put back*, not *where it
goes*. So the old rule still holds, and `/safecall:before` says it out loud: do not hand over a
folder you would not post to a stranger. What to show and what to keep back is a separate question,
and the plugin helps you ask it rather than answering it for you.

## Requirements

Claude Code with plugin support, and `python3` on the machine (macOS and most Linux have it; on
Windows install it from python.org or the Microsoft Store).

## Licence

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
