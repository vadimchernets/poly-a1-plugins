#!/bin/sh
# Keeps the copies of safecall and duocall in this catalogue in step with their working folders.
#
# Why a check and not just a copy: a plugin reaches the person by TWO roads - inside the paid
# Poly A1 kit (`assets/kit/*.zip`, built by `site/build-kit.sh` straight from
# `~/Developer/<plugin>`) and from here, via `/plugin marketplace add`. If the two copies drift
# apart, the buyer gets one thing in the folder and another from the install line, and nobody
# would tell them. build-kit already caught exactly this drift in chasecall on 25.09.2026 - two
# files within a day.
#
#   ./sync.sh          - copy from the working folders into here
#   ./sync.sh --check  - change nothing, fail if anything drifted (run before publishing)

set -u
HERE=$(cd "$(dirname "$0")" && pwd)
SRC_ROOT=${SRC_ROOT:-"$HOME/Developer"}
PLUGINS="safecall duocall"
EXCL="--exclude=.git --exclude=.DS_Store --exclude=._* --exclude=__pycache__ --exclude=*.pyc"

check=0
[ "${1:-}" = "--check" ] && check=1

problems=0
for p in $PLUGINS; do
  src="$SRC_ROOT/$p"
  if [ ! -d "$src" ]; then
    echo "BAD: working folder $src is missing"
    problems=$((problems + 1))
    continue
  fi
  if [ "$check" -eq 1 ]; then
    # shellcheck disable=SC2086
    diff=$(rsync -rn --delete --itemize-changes $EXCL "$src/" "$HERE/$p/" 2>/dev/null)
    if [ -n "$diff" ]; then
      echo "BAD: $p here has drifted from $src:"
      echo "$diff" | sed 's/^/    /'
      problems=$((problems + 1))
    else
      echo "  $p - in step"
    fi
  else
    # shellcheck disable=SC2086
    rsync -a --delete $EXCL "$src/" "$HERE/$p/"
    echo "  $p - copied"
  fi
done

# Every plugin must have a manifest, otherwise Claude Code sees loose files, not a plugin.
for p in $PLUGINS; do
  [ -s "$HERE/$p/.claude-plugin/plugin.json" ] || {
    echo "BAD: $p/.claude-plugin/plugin.json is missing"; problems=$((problems + 1)); }
done

# And every plugin the catalogue names by a relative path must exist.
python3 - "$HERE" <<'PY' || problems=$((problems + 1))
import json, sys, os
root = sys.argv[1]
m = json.load(open(os.path.join(root, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
bad = 0
for p in m["plugins"]:
    s = p["source"]
    if isinstance(s, str):
        if not os.path.isdir(os.path.join(root, s)):
            print(f"BAD: the catalogue promises {p['name']} at {s}, but the folder is missing"); bad = 1
    elif s.get("source") == "github" and not s.get("repo"):
        print(f"BAD: {p['name']} has a github source without repo"); bad = 1
print(f"  catalogue: {len(m['plugins'])} plugin(s), paths checked")
sys.exit(bad)
PY

echo
if [ "$problems" -eq 0 ]; then
  echo "sync: 0 problems"
  exit 0
fi
echo "sync: $problems problems"
exit 1
