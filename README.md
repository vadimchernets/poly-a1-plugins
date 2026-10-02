# Poly A1 plugins

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23107737.svg)](https://doi.org/10.5281/zenodo.23107737)

**Pay $5 once — that's it: two AIs from different companies work together right on your phone. ChatGPT answers, Claude checks. No paid keys, no servers, no computer, nothing more to pay.**

Have ChatGPT and Claude? Start right away. Have one? It helps you install the other. Have neither? Gemini (Google) or Meta AI (WhatsApp, Facebook) helps you install both, free.

<details>
<summary><b>How it works</b></summary>

The orchestration runs on the phone itself. iPhone: a Shortcut calls Ask ChatGPT, then Ask Claude — actions the apps publish themselves; answers pass between your own apps, with no server of ours and no API keys, on your own accounts — free ones are enough. Android: the phone calls free AIs (Groq, OpenRouter, Google AI Studio) directly with your free key — no card, no server of ours; or by hand with your ChatGPT and Claude. Nothing like it exists anywhere else.

</details>

The phone part is [Duo and Trio](https://github.com/vadimchernets/c1m-duo); this repository is the computer part of Poly A1.

Four small additions to [Claude Code](https://claude.com/claude-code) for a person who is not a
programmer.

## Installing

Published on 26.09.2026. Add it by name, and corrections made after today reach you:

```
/plugin marketplace add vadimchernets/poly-a1-plugins
/plugin install safecall@poly-a1
/plugin install duocall@poly-a1
/plugin install pocketcall@poly-a1
/plugin install chasecall@poly-a1
```

Or point Claude Code at a local copy of this folder — that path needs no network and no account:

```
/plugin marketplace add /path/to/poly-a1-plugins
/plugin install safecall@poly-a1
/plugin install duocall@poly-a1
/plugin install pocketcall@poly-a1
/plugin install chasecall@poly-a1
```

The same works from the Poly A1 folder for the computer: all four ride inside it, with their own
catalogue at the root, and install with no network at all. Checked on a real machine on 26.09.2026 —
all four come up enabled.

`pocketcall` and `chasecall` are listed here from their own published repositories, so from **this**
folder they resolve over the network; from the Poly A1 folder they resolve locally.

## The step everybody misses

**Auto-update is OFF by default for any marketplace that is not Anthropic's own.** There is no
field in `marketplace.json` that can turn it on — only the person can, and if they do not, they stay
on the version they first installed, for ever.

So after adding it by name, do this once:

```
/plugin
```

→ **Marketplaces** tab → this marketplace → **Enable auto-update**.

Without it, every correction made here after that day never reaches that machine. It is deliberately
**not** offered to buyers before publication: an auto-update switch pointing at a 404 updates
nothing and teaches them the product is broken.

## What is in it

| | |
|---|---|
| **safecall** | Nothing is written before a copy exists; nothing is read before you have seen the list; no answer ends without saying what nobody checked. Plus three ready readings of a document — where the catch is, what a plan is missing, what here is fact and what is opinion. |
| **duocall** | A second opinion from a **different company's** AI, and an honest account of where the two disagreed. Two AIs agreeing is not proof, and it says so. Works through a free browser chat when there is no second program. |
| **pocketcall** | Leave the computer working and take the phone — the seven silent reasons an evening away never works, checked before you go out of the door. |
| **chasecall** | Something nobody is answering — a refund, a booking, a request. It keeps the task between sessions, writes the next letter, counts the attempts, and says when the call is yours to make. |

`safecall` and `duocall` live in this repository. `pocketcall` and `chasecall` are listed here but
kept in their own repositories, so there is exactly one copy of each in the world and this
marketplace cannot drift from it.

## What none of them do

No account. No API key. No second subscription. Nothing bought, and nothing that suggests buying.
They drive only what is already installed and already signed in on the machine. Python 3.8+ and the
standard library, no dependencies.

None of them makes Claude Code private: what Claude Code reads still goes to Anthropic. These
plugins decide whether a change can be undone and whether an answer can be trusted — not where the
text goes.

## For the buyer of Poly A1

All four also ride **inside** the Poly A1 folder for the computer, so they work with no network and
no GitHub account at all. This marketplace exists for the other thing: getting corrections after the
day you bought it.

## Keeping this repository in step

`safecall` and `duocall` are developed in `~/Developer/safecall` and `~/Developer/duocall` and
copied here. `./sync.sh` copies them in and `./sync.sh --check` fails if this repository has drifted
from them — run the check before publishing, or the marketplace will hand people an older plugin
than the paid folder contains.

## Licence

Apache-2.0 for all four. Each plugin carries its own `LICENSE` and `NOTICE`.

---

<sub>Free Claude has a daily limit. Ran out and you like Claude? Claude Pro ($20/month, $17 billed yearly; paid to Anthropic, not us) lifts it. While you wait, a free AI on a key does the checking (Trio).</sub>
