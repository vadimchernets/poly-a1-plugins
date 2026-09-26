---
name: undo
description: Put the person's files back the way they were before you changed them. Use this the moment they say anything like "верни как было", "put it back", "undo that", "ты испортил", "отмени", "I don't like it, go back" - and use it before arguing that the change was correct. Also use it when they sound frightened about what just happened to a file.
argument-hint: "[which copy, if not the most recent one]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py *) Read
---

# Safecall: put it back the way it was

The user said: $ARGUMENTS

Answer in the person's language. **Do this first and explain afterwards.** A person who says "верни
как было" is frightened, and an explanation before the undo reads as an argument.

## 1. Show what can be put back

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py" list --folder "<the folder>"
```

Say the list in dates and file names, not in numbers of snapshots:

> Могу вернуть к тому, как было сегодня в 14:20 — это письмо и таблица.

## 2. Show what would change, then do it

Run it once without `--yes`. That changes nothing and prints exactly which files would come back.
Show that to the person. Then, once they say yes:

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py" restore --yes --folder "<the folder>"
```

Add `last` or a number to pick an older copy.

## 3. Tell them the undo is also undoable

The script copies the current state before overwriting it. Say so — it is the sentence that lets a
frightened person actually press yes:

> Вернул, как было в 14:20. То, что было до возврата, я тоже сохранил — если передумаете, верну обратно.

## 4. If there is no copy

Do not hide it and do not blame them. Say it plainly, then say what still exists:

> Копии этого файла у меня нет — я начал менять его до того, как её сделал. Это моя ошибка.

Then look for what is genuinely recoverable and say which of these the person has, in their words:
the Mac's own Time Machine, the Windows "Previous Versions" of a folder, the cloud folder's own
version history (iCloud, OneDrive, Google Drive, Dropbox all keep one), or the file still being
open and unsaved in a program. Name the one that fits their machine and walk them to it.

Then make a copy of whatever is left, immediately, before doing anything else.
