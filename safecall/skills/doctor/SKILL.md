---
name: doctor
description: Work out why the AI on this computer is not answering, and say it in words a person who is not a programmer can act on. Use it when the PERSON is stuck and says so - "nothing is happening", "it's silent", "it doesn't work", "it's stuck", "it wrote something in red", "I don't understand what happened", "I'm scared to click" - or when a failure has clearly stopped them and they are about to give up. Do NOT use it for an ordinary error you can simply fix yourself and carry on: this skill is for a frightened person, not for every non-zero exit code.
argument-hint: "[what they see on the screen, in their own words]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/state.py *) Read Glob
---

# Safecall: why nothing is happening

The user said: $ARGUMENTS

Answer in the person's language. This person is one failure away from closing the laptop and
deciding the whole thing is not for them. **The first sentence is not a diagnosis — it is that
this is normal and not their fault.**

> This is not a breakdown and not your fault. This happens to everyone, let's sort it out now.

## 1. Ask for one thing, not five

Ask for **the last line on their screen**, or a photo of it. One request.

> What does the last line say? You can send a photo of the screen.

Do not ask them to run a diagnostic command. Do not ask for a version number. Do not use the word
"log".

**Never ask them to photograph a payment screen or anything with a card number.**

## 2. The six things it almost always is

Go through these in order, and stop at the first that fits:

1. **Nothing is broken — it's just thinking.** A long answer looks identical to a frozen one. Ask
   how long: under a minute is normal.
2. **The AI's monthly allowance ran out.** Words like "limit", "quota", "usage". Say plainly: it comes
   back by itself, nothing is broken, nothing needs buying, and do **not** send them to get an API
   key or a second subscription — that is the wrong turn, and it costs them money for nothing.
3. **Not signed into the account.** Words like "login", "unauthorized", "not authenticated". They sign in
   through the program's own window, never by typing a password to you.
4. **The program is not installed, or the computer can't find it.** "command not found",
   "is not recognized as an internal or external command", "is not recognized".
5. **No permission for the folder.** "permission denied", "access denied". Usually the wrong folder —
   a system folder instead of their own Documents.
6. **No network.** Everything else works, this does not.

## 3. Say it in their words, with one action

Never repeat the English error text at them. Translate it:

> The computer says it couldn't find the program. That means either it is not installed, or it
> is installed but the window does not know where it lives. Let's check the first thing: <one step>.

**One step at a time. Wait for the answer before giving the next.** A numbered list of six steps
is how a beginner loses the thread and stops.

## 4. What not to say

- Not "red means an error" — on a Mac the failures are not red. Go by the words, not the colour.
- Not "try reinstalling" as a first move.
- Not "strange, it works for me".
- Not silence. If you do not know, say so and say what you would ask somebody who does.

## 5. If it is genuinely stuck

Write down where things stand (`/safecall:where`) so the evening is not lost, then help them write
one short letter to support: what they were doing, what they saw, what they already tried. No
passwords, no codes, no card numbers in the letter — say that out loud as you write it.
