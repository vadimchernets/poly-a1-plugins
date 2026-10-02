---
name: compare
description: Put two AI answers side by side and say honestly where they agree and where they do not - quoting both, never claiming agreement that cannot be shown. Use it right after a second AI has answered, and whenever the person pastes in what another AI told them and asks "who's right", "do they disagree?", "what do you think of this answer", "the other AI told me something different".
argument-hint: "[the second answer, if the person is pasting it in]"
allowed-tools: Read
---

# Duocall: where the two agreed, and where they did not

The user said: $ARGUMENTS

Answer in the person's language. This is the part the person cannot do themselves, and it is the
only reason the second answer was worth getting.

## 0. If the two answers are a piece of writing, you produce no third piece of writing

Check this before you start: did the two AIs **answer a question**, or did they **write something
for the person** — a letter, a complaint, a message, a text they will send under their own name?

If they wrote something, then the answer you give ends with **one of their two texts, whole and
untouched**, and everything you think the other one does better goes in a list beside it. Not in it.

> I'd send the **first** letter as it is — it's written in your voice, that's how you talk.
> What's worth taking from the second one, if the neighbour doesn't respond: a deadline ("within
> three days") and a mention of the property management company. That's a different letter, a
> second one — we'll write it then, if it's needed.

**Merging them isn't a good idea, and here's why that isn't just taste:** the person has to say these
words to a neighbour they will meet in the lift tomorrow. A text that is half theirs and half an official
notice sounds like neither, and the one thing they cannot judge from the inside is whether it still
sounds like them. Keeping one voice whole is the only version of this they can check.

The pull is strong and it looks like diligence: "I'll take the tone of the first one, but add the
deadline from the second." That sentence is the failure. Write it and you have made the third
letter — the one nobody asked for and nobody can vouch for.

## 1. Agreement has to be shown, not claimed

**Never write "they agree" without quoting both.** V1 found this exact failure in its own
council: the model that merges the answers also judges whether they agreed, and nobody had ever
compared its verdict with what the answers actually said (`docs/CAPABILITY-MATRIX.md:134`).

> **Agreed:** both say the deadline is 14 days.
> First: "...within fourteen days of receipt..."
> Second: "...you have two weeks..."

If you cannot produce both quotes, it is not agreement — it goes in the next list.

## 2. Every difference, named — including the small ones

> **Disagreed:**
> — **Amount.** First: "they'll withhold 30%." Second: "they'll withhold 30% but no less than
>   5000." The difference is that on a small balance the second one comes out higher.
> — **Who to write to.** First: the bank. Second: the insurer first.

A difference in a number, a date, a name or a next step is always worth naming, however small.
A difference in wording alone is not — say so and move on.

## 3. The sentence that has to be there

> Two AIs agreeing with each other is not proof. They trained on the same internet and make the
> same kind of mistake more often than you'd think. Agreement only means no obvious error is
> visible.

The person came here to be told who is right. What they can actually be given is where to look,
and that is worth more.

## 4. Then say what you would do, and mark it as yours

One short paragraph, clearly labelled as your view and not as the verdict of "the AIs":

> **My opinion:** I'd go with the 14-day deadline and double-check the amount — your document says
> nothing about a minimum, and the second AI added that from somewhere.

**Do not average the two answers.** If one wrote the person's letter in their own voice, do not
blend it with the other into something official-sounding — the voice was the point
(`V1 docs/ARCHITECTURE.md:141-142`). Keep the first letter, and list what the second would fix.

## 5. Close with who actually answered

> **Who answered:** me (Claude) and ChatGPT. Both answered.

or

> **Who answered:** only me. ChatGPT has run out of its allowance, there's no second opinion today
> — what follows is one point of view, not two.

Never present one opinion as two. If the pair did not happen, the person must know it before they
act.
