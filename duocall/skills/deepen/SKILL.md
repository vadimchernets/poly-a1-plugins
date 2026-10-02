---
name: deepen
description: Go back to the AIs about the disputed points only, keeping the answers they already gave. Use it after a comparison has found a real disagreement and the person asks "so who's right", "how can I find out", "which one of them", "how do I settle this", "let's figure it out". Do not use it when the two agreed - there is nothing to settle.
argument-hint: "[which disagreement, if there was more than one]"
allowed-tools: Bash(python3 ${CLAUDE_PLUGIN_ROOT}/scripts/second.py *) Read
---

# Duocall: settle only what is actually in dispute

The user said: $ARGUMENTS

Answer in the person's language.

*(If the person asked for a **third AI** — "two against one," "let's ask a third" — that sentence
is answered too, and first. The words are in §5 at the end. It is two lines added to the answer
below, never a replacement for it.)*

## 1. Why this is not "just ask again"

Retyping the whole question costs every AI a full answer and usually returns the same split in
different words. V1 built a button for exactly this and said why: a person who reads "the first one
said 600, the second said 800" can otherwise only ask everything again (`docs/CAPABILITY-MATRIX.md:135`).

So: **the first answers stay. Only the disputed point goes back.**

Never delete or overwrite what they already said. If the second round contradicts the first, the
person sees both and that fact is itself information.

**And the failure that looks most like helpfulness: answering it yourself instead.** Asked "who's
right," it is very tempting to settle it out of your own knowledge, announce a winner, and bring in
numbers that are in neither answer. That is not a second round — it is a third opinion delivered as
a verdict, and it quietly throws away the only thing the person actually paid two AIs for.

Before you write a word, say which of these you are doing, and say it to the person too:

- **narrowing** — sending the one disputed point back. This is the skill.
- **adding your own view** — allowed, but only *after* the two are laid out, and marked as yours:
  "this is my opinion, a third one, not an answer to who's right."

If a number appears in your answer that is in neither of theirs, you have left this skill. Either
quote where it came from, or take it out.

## 2. Ask a narrow question, and ask it of both

One disputed point, one question, and it names the disagreement without naming who said what — a
model told "the other AI said X" will often just concede:

> The question was: <the original question>. There's a disagreement on one point: <the disputed
> point>.
> Answer only this: <narrow question>. If the original document has no answer — say so.

**And say to the person, out loud, that the rest stands.** One line, and it is not filler — it is
the whole difference between this and asking everything again:

> Everything else they agreed on **stays as it is** — I'm only re-asking about the disputed point.

Without it the person assumes the two answers have been thrown away and the evening starts over.
The narrow question above is what you send; this line is what you say. Both, always.

Send it to the second AI with `second.py ask -`, and answer it yourself, separately, before you
read theirs. **Answering after reading theirs is not a second round, it is agreement.**

## 3. The three ways this ends, and all three are fine

1. **One of the two corrected itself** — say who and why, and say what convinced them.
2. **Both stuck to their guns.** Then the honest answer is that this cannot be settled between
   AIs, and you say what *would* settle it: the exact line of the document, the page to open, the
   person to ring.
3. **Both were wrong.** It happens, and it is the most valuable outcome of the whole exercise.

## 4. Never manufacture a winner

If the disagreement is still standing, say so in one line and give the person the step that ends
it — not a guess dressed as a conclusion:

> They still didn't agree. That means the document doesn't settle the question, and guessing isn't
> allowed here. Call <who> and ask exactly one thing: <question>.

One escalation, not two. If the person wants a third AI, say plainly that a third opinion makes the
picture wider, not more certain — and that two of three agreeing still is not proof.

## 5. When they ask for a third AI

"Let's ask a third one, then it'll be two against one" is the commonest thing a person says here.
It gets answered — **two lines at the top of your reply, and then you carry on with §1–§4 exactly
as if they had not said it.** Not answering it is worse than refusing: they will go and ask the
third AI anyway, and this time without you.

The two lines, and they never start with "yes":

> A third AI makes the picture **wider**, not more certain — two out of three agreeing still isn't
> proof: they can be wrong in the same direction, because they trained on the same internet.
> A dispute isn't settled by a majority but by the document or whoever is responsible for the
> answer: **call** <who> and ask exactly one thing: <question>.

Both halves are obligatory. **"Wider, not more certain"** on its own is a refusal, and a refusal with
nothing after it sends the person straight to the third AI. **The step that actually ends it** on
its own skips the thing they got wrong. Two lines, both of them.
