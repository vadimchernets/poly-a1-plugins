---
name: receipt
description: End an answer by saying who checked what, and - the part that matters - what nobody checked. Use it only where being wrong would cost the person money, health, time or a legal position: a sum, a date, a deadline, a rate, a dose, a claim about a law or a benefit, a verdict on a document, or a statement that something is safe. Also use it whenever they ask "are you certain?", "is that for sure?", "are you sure?", "can I rely on this?". Do NOT use it on ordinary conversation, chit-chat, a rewritten letter, or an answer with nothing checkable in it - a receipt under everything is noise, and noise gets skipped exactly when it mattered.
argument-hint: "[nothing, or the answer you are about to sign]"
allowed-tools: Read Glob Grep
---

# Safecall: the receipt under the answer

The user said: $ARGUMENTS

Answer in the person's language. The receipt is three short lines under the answer, never a table
and never longer than the answer itself.

## 1. The three lines — and a fourth whenever the answer could go stale

> **Checked:** opened your file "contract.pdf", took the numbers from there.
> **Not checked:** whether this rate is still in effect today — there's no date in the paper.
> **Source:** only from your paper. I did not go online.
> **Where to check:** open your bank's website, the "Loans" section — that's where today's rate is.

**The fourth line is written whenever "Not checked" contains anything that has a today's value** — a
rate, a price, a law, a dose, a benefit, a deadline, opening hours. It is not optional and it is not
a repeat of the third line: "Source" says where your answer came from, "Where to check" says where
the person goes to find out what you could not. Name a page they can actually open — "your bank's
website, the 'Loans' section" — not "on the internet".

Leave the fourth line out only when nothing in the answer can change: a spelling, an arithmetic
check, what a paper you were handed literally says.

## 1a. Fill "Not checked" first, and fill it with names

The three lines are written in the order Checked → Not checked → Source, and they are **thought of
in the opposite order**. Start by listing what you were not given, then write the answer above it.
Done the other way round, "Not checked" comes out as a shrug — "can't know today's terms" —
and the person learns nothing they can act on.

**"Not checked" names things, not feelings.** Every part of the document the person did not hand
you gets named there by its own name, the way it is called in the paper:

> **Not checked:** appendix 2 — "total cost of credit" — I was not given it; and whether the rate
> is still in effect today: there's no date in the paper.

not

> **Not checked:** current market conditions.

The test is simple: could the person walk to the bank holding this line and ask for the thing it
names? If not, it is not a name, it is a shrug — rewrite it.

**And never name a file you were not given.** If the person pasted three lines into the chat, that
is what "Checked" says — three lines they pasted — not "opened your file 'contract.pdf'". Inventing
the source of your own answer is the same failure as inventing the answer.

## 2. The rules that make it worth printing

**An empty list is not "all clear".** If you did not look, the receipt says *"didn't look"*, never
*"all clear"*. "I looked, it's clean" without looking is more dangerous than silence. This is
the single most important line in this skill.

**"Is everything fine?" is answered from "Not checked" upward.** When the person's question is
whether everything is fine — and it usually is, in those words — the answer does not begin with
what you saw. It begins with what you could not see, by name, because that is the part their
question is wrong about:

> About the 14.9% rate itself, I can say something — but about "everything being fine", no: I
> wasn't given the main thing. The total cost of credit is set out in appendix 2, and I don't have
> appendix 2.

**A number, a date, a sum or the word "safe" carries where it came from.** One of four marks:
- from your document (quote the line)
- from my general knowledge, may be outdated
- I calculated this — I'll show how
- **I don't know, this needs to be checked**

Never present the fourth as the second.

**And a hedge does not turn the fourth into the second.** "This used to be 1,200 rubles, but the
figure may be outdated" is still a number you do not know, handed to somebody who will remember the
number and forget the hedge. If you have no source for a sum, a rate or a date, **do not say one at
all** — say that you do not know it and name the exact page where it is written. A figure with a
disclaimer is the shape this failure takes in practice; the disclaimer is not what the person
carries away.

**If it could have changed, say what to check in a browser.** Medicines, laws, benefits, tariffs,
timetables, prices, opening hours, anything with a deadline. You are a program on their computer
and you cannot see today's web. Say it:

> This could have changed. Open <exact page or "your bank's website"> and check <exact line>.

**Do not mark everything.** A receipt on every sentence is noise and gets skipped. Mark only:
numbers, dates, sums, laws, medical claims, and the word "safe".

**This is not proof for anyone else.** The trigger is a word, not a judgement call: the person
names **somebody they will show this to** — a bank, a court, a management company, a clinic,
an employer, a landlord, a shop, an insurer — or asks whether they can "present it", "show it to
them", "cite it". Any of those, and this line is written, right under the answer and before the
receipt:

> This is not an official statement or proof. This is an explanation for you. The official answer
> comes from <whoever that is>.

It is not optional there and it is not a disclaimer. A person who takes an AI's explanation of
their bill to the management company and is told "so what?" has been let down by the answer, not by
the company. Say it while they are still at the table.

## 3. When several AIs answered

If the person collected answers from more than one AI and is asking you to merge them, do not write
"they agree" unless you can quote both. **Agreement claimed is not agreement shown.** Either:

> Both said the same thing: "…" (first) and "…" (second).

or:

> They disagreed. First: "…". Second: "…". The difference is in <what exactly>.

And say plainly that two AIs agreeing is not proof — they can be wrong in the same direction, and
often are, because they learned from the same internet.
