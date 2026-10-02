---
name: undo
description: Put the person's files back the way they were before you changed them. Use this the moment they say anything like "put it back the way it was", "put it back", "undo that", "you broke it", "undo it", "I don't like it, go back" - and use it before arguing that the change was correct. Also use it when they sound frightened about what just happened to a file.
argument-hint: "[which copy, if not the most recent one]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py *) Read
---

# Safecall: put it back the way it was

The user said: $ARGUMENTS

Answer in the person's language. **Do this first and explain afterwards.** A person who says "put
it back the way it was" is frightened, and an explanation before the undo reads as an argument.

## 1. Show what can be put back

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py" list --folder "<the folder>"
```

Say the list in dates and file names, not in numbers of snapshots:

> I can return things to how they were today at 2:20pm — that's the letter and the spreadsheet.

## 2. Show what would change — and say, in the same breath, that the return is itself returnable

Run it once without `--yes`. That changes nothing and prints exactly which files would come back.

**The question and the reassurance are one message, in this order, and neither goes without the
other.** This is not a style rule. The person is frightened *at the moment you ask*, and a promise
delivered after they have already said yes arrives too late to have been any use:

> These files will come back: "letter-to-bank.docx", "expenses.xlsx" — as they were today at
> 2:20pm.
> What's there now, I'll save before putting them back — **if you change your mind, I'll bring
> it back.**
> Shall we put it back?

Three lines, always all three: **what comes back, by name · the return is undoable · the question.**
If your draft has the question but not the middle line, it is not finished — add the line, do not
send it. Then, once they say yes:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py" restore --yes --folder "<the folder>"
```

Add `last` or a number to pick an older copy.

## 3. After the return, say it once more

The script copies the current state before overwriting it, so the sentence is still true afterwards
and still worth saying:

> Put it back the way it was at 2:20pm. What was there before the return, I saved that too — if
> you change your mind, I'll bring it back.

## 4. If there is no copy

Do not hide it and do not blame them. Say it plainly, then say what still exists:

> I don't have a copy of this file — I started changing it before I made one. That's my mistake.

Then look for what is genuinely recoverable and say which of these the person has, in their words:
the Mac's own Time Machine, the Windows "Previous Versions" of a folder, the cloud folder's own
version history (iCloud, OneDrive, Google Drive, Dropbox all keep one), or the file still being
open and unsaved in a program. Name the one that fits their machine and walk them to it.

Then make a copy of whatever is left, immediately, before doing anything else.

## If `python3` is not on this machine

On Windows it often is not, or the name opens the Microsoft Store instead of running anything.
**This is not the person's fault and it is not a broken plugin.** Try `py -3` and then `python` in
place of `python3`; if none of them runs, say so in one plain line and carry on doing the job by
hand — you can still read the folder, still say what you are about to change, still be careful.
What you must never do is show them a Python error and stop.

> There is no Python on this computer, so I cannot turn on the automatic safety net. I will keep
> going and will warn you in words before every change.
