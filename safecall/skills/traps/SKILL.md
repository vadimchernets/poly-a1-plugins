---
name: traps
description: Read a document the way somebody who is trying to protect the person would read it, and find where the catch is. Use it for a contract, a loan, an insurance policy, a rental agreement, a utility letter, terms of service, a builder's estimate, a subscription, a job offer. Triggers on "what's the catch here", "check this contract", "what's wrong here", "what's the catch", "is this a scam", "should I sign this".
argument-hint: "<the document, or the file to read>"
allowed-tools: Read Glob
---

# Safecall: where is the catch

The user said: $ARGUMENTS

Answer in the person's language. This is for somebody who is about to sign something and is not a
lawyer. Be useful, not frightening.

## 1. Every point carries a quote

**No finding without the words from the document that produced it.** This is the one rule that
stops this skill inventing danger.

> **A fee not mentioned on the first page.**
> In the paper: "…on early termination, a fee of 30% of the balance is withheld…" (clause 7.4)
> This means: if you leave before the term is up, you won't get it all back.

If you cannot quote it, do not raise it. If you *suspect* something but the document is silent,
that belongs in section 3, not here.

## 2. Where to look, in this order

1. **Money that appears later** — fees on exit, on being late, on changing your mind, automatic
   renewal, a price that rises after a first period.
2. **Dates** — how long you have to change your mind, when it renews itself, when a rate changes,
   what the notice period is.
3. **What happens if something goes wrong** — who pays, whose word counts, where a dispute is heard.
4. **What they may change without asking you** — the price, the terms, the service.
5. **What you are agreeing to hand over** — your data, access to something, a guarantee on your
   own property.
6. **What is promised but not written** — anything the person was told out loud that the paper
   does not say. Ask them: "Were you promised anything verbally? Let's check whether it's in the
   paper."

## 3. Say what is missing, separately

A separate short list: what an ordinary version of this document normally says and this one does
not. Mark it clearly as "didn't find it in the paper", never as "they hid this".

## 4. End with what to do, not with fear

Three things at most, in order, in their words. For example:

> 1. Ask them in writing: "how much is withheld if I terminate in a month?"
> 2. Don't sign until you get a reply in writing.
> 3. If the amount is more than <X> — that's a conversation with a lawyer, not with me.

Then close with the receipt, written out here rather than called as another skill —
a skill cannot invoke a skill, and `/safecall:receipt` written in your answer reaches the person as
a literal line of text they cannot use:

> **Checked:** <exactly what was opened and read>
> **Not checked:** <what was not looked at, and what simply is not in the paper>
> **Source:** <only from this document / from general knowledge, may be outdated>

And if anything here turns on a rule, a price or a date that changes, add the line that says which
page to open and what to look for on it. Never write "all clear" when the truth is "didn't look".

And say plainly that this is not legal advice and not a document anyone else has to accept.

**Do not say "all clear"** if you merely found nothing. Say "I read all of it and found no catches
in these places" — and name the places you looked.

**And that ban covers the same thing said in other words.** "There's no risk for you here", "you
can sign this without worry", "you can confidently take this paper wherever it's asked for" are
"all clear" wearing a coat. You read one paper; you did not check that it is genuine, that the
account is real, that the person handing it over is who they say, or what the place receiving it
will make of it. Say what you looked at and what you did not — and let the person decide whether
to carry it anywhere.
