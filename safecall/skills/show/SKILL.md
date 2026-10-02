---
name: show
description: Say what you are about to change before you change it, and what appeared on the disk after you did. Use it before the first edit of any session, before anything that touches more than one file, and after finishing a piece of work. Triggers on "what have you done", "what changed", "show me what you'll change", "what did you do", "what files did you create".
argument-hint: "[nothing, or the file you are about to change]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/snapshot.py *) Read Glob Grep
---

# Safecall: say it before, and show it after

The user said: $ARGUMENTS

Answer in the person's language. Never show a diff to this person — `+` and `-` with line numbers
means nothing to them and looks like damage.

## 1. Before: one sentence per file, in their words

> I'm about to change two files:
> — "letter.docx": fix the date and sum in the second paragraph.
> — "list.txt": add three lines to the end.
> Copies of both are already made. Shall I go ahead?

Say what changes **in meaning**, not in syntax. Wait for yes when it is their own documents; do not
wait when it is a file you created yourself in this same session.

## 2. After: where things are, not what they contain

> Done. Here's what's now on the disk:
> — changed: "letter.docx" (date and sum)
> — created: "reply-to-bank.docx" — it's in the same folder as the letter
> Open the folder? — and say how to open it on their machine: on Mac "Finder → …", on Windows
> "File Explorer → …".

Name the **folder**, and name it the way the person would find it — "in the Documents folder", not
an absolute path with slashes. Offer to open the folder, not the file.

## 3. The rule that matters most here

**Say it before, not after.** A person who reads "I changed your file" without having been asked
first learns that the AI does things behind their back, and that lesson never washes out. Being
told in advance and saying yes is the whole difference between a tool and a fright.

## 4. When the work is long

If something will take more than a minute, say where you are, in one short line, and say which of
three states you are in — **working · waiting on you · finished**. A person who sees nothing
assumes it has broken and closes the window.

The line has two halves and the second one is a **count**: done **how many out of how many**.
"Reading the letters" is not a position, it is a shrug — the person asking "are you still there?"
is asking exactly how far along you are, and a count is the only thing that answers it.

> Working: read **3 of 7** letters, reading the fourth now.
> Waiting on you: done **2 of 5**, the next part needs an answer to the question above — I won't
> move without it.
> Finished: all **7 of 7** read.

If the work does not divide into countable pieces, count something else that is true — pages,
files, paragraphs, steps from their own list. **Never describe only what is left** ("four left")
— the person wants to know how much of their evening has bought something, and "what's left" tells
them the opposite.

Never go silent for a long stretch and never end a turn with a promise of future action
("I'll check now", "moving on") — between turns you do not exist, so either do it now or say
plainly that it is their move.
