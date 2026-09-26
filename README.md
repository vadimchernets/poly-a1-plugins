# Poly A1 plugins

Four small additions to [Claude Code](https://claude.com/claude-code) for a person who is not a
programmer.

## Installing today: from the folder, not from GitHub

**This repository is not published yet**, so `/plugin marketplace add vadimchernets/poly-a1-plugins`
returns a 404. Until the owner publishes it, the working path is the local one — clone or copy this
folder, then point Claude Code at it:

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

## After the owner publishes: the step everybody misses

**Auto-update is OFF by default for any marketplace that is not Anthropic's own.** There is no
field in `marketplace.json` that can turn it on — only the person can, and if they do not, they stay
on the version they first installed, for ever.

So once this repository is public and added by name, do this once:

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
