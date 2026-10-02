#!/bin/sh
# Keeps this catalogue pinned to what each plugin has actually published.
#
# Since 02.10.2026 this repository holds no plugin code at all: every entry in
# `.claude-plugin/marketplace.json` points at that plugin's own public repository, pinned to a commit.
# One copy of each plugin in the world, one catalogue. The paid Poly A1 kit generates its own
# catalogue from this very file (`poly-a1/site/kit-marketplace.py`), with the sources turned into the
# folders that ride inside it - same name `poly-a1`, same versions. That sameness is what lets a buyer
# switch from the kit folder to this catalogue without losing a plugin (OFFER-THESE.md).
#
# Before, safecall and duocall were COPIED here, and the copies drifted (README and .zenodo.json, found
# 02.10.2026); the catalogue listed four plugins of six; and the kit's catalogue was a third file with
# versions three releases behind. This script exists so none of that can happen silently again.
#
#   ./sync.sh          - pin every entry to its working repository's HEAD and plugin.json version
#   ./sync.sh --check  - change nothing, fail if any pin or version is behind (run before publishing)
#
# A pin is written only for a commit that is already on GitHub: a catalogue pointing at an unpushed
# commit would hand people an install that fails.

set -u
HERE=$(cd "$(dirname "$0")" && pwd)
SRC_ROOT=${SRC_ROOT:-"$HOME/Developer"}
mode=write
[ "${1:-}" = "--check" ] && mode=check

python3 - "$HERE/.claude-plugin/marketplace.json" "$SRC_ROOT" "$mode" <<'PY'
import json, os, subprocess, sys

path, src_root, mode = sys.argv[1:4]
with open(path, encoding="utf-8") as fh:
    m = json.load(fh)

def git(repo, *args):
    try:
        return subprocess.check_output(["git", "-C", repo] + list(args), text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None

bad = 0
changed = 0
for e in m["plugins"]:
    name = e["name"]
    work = os.path.join(src_root, name)
    src = e.get("source")
    url = "https://github.com/vadimchernets/%s.git" % name
    # https, not `github`: a `github` source clones over SSH when the machine has any SSH setup,
    # and a buyer without a GitHub key then gets "Permission denied (publickey)" (seen live 02.10.2026).
    if not (isinstance(src, dict) and src.get("source") == "url" and src.get("url") == url and src.get("sha")):
        print("BAD: %s - the source must be {source: url, url: %s, sha: <commit>}" % (name, url)); bad += 1
        continue
    if not os.path.isdir(os.path.join(work, ".git")):
        print("BAD: %s - working repository %s is missing" % (name, work)); bad += 1
        continue
    if git(work, "status", "--porcelain"):
        print("BAD: %s - %s has unpublished edits" % (name, work)); bad += 1
        continue
    head = git(work, "rev-parse", "HEAD")
    upstream = git(work, "rev-parse", "@{upstream}")
    if not head or head != upstream:
        print("BAD: %s - HEAD of %s is not what GitHub has (push it first)" % (name, work)); bad += 1
        continue
    with open(os.path.join(work, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        version = json.load(fh).get("version")
    if src["sha"] == head and e.get("version") == version:
        print("  %s %s - pinned to %s, in step" % (name, version, head[:7]))
        continue
    if mode == "check":
        print("BAD: %s - catalogue says %s @ %s, the published plugin is %s @ %s"
              % (name, e.get("version"), src["sha"][:7], version, head[:7])); bad += 1
    else:
        src["sha"] = head; e["version"] = version; changed += 1
        print("  %s %s - pinned to %s" % (name, version, head[:7]))

if mode == "write" and changed and not bad:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(m, fh, ensure_ascii=False, indent=2); fh.write("\n")
print("  catalogue: %d plugin(s)" % len(m["plugins"]))
sys.exit(1 if bad else 0)
PY
rc=$?

if command -v claude >/dev/null 2>&1; then
  claude plugin validate "$HERE" >/dev/null 2>&1 || { echo "BAD: claude plugin validate fails on this catalogue"; rc=1; }
fi

echo
[ "$rc" -eq 0 ] && { echo "sync: 0 problems"; exit 0; }
echo "sync: problems found"
exit 1
