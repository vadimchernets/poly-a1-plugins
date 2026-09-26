#!/bin/sh
# Держит копии safecall и duocall в этом каталоге вровень с рабочими папками.
#
# Зачем проверка, а не просто копирование: плагин уезжает к человеку ДВУМЯ дорогами — внутри
# платного набора Poly A1 (`assets/kit/*.zip`, его собирает `site/build-kit.sh` прямо из
# `~/Developer/<плагин>`) и отсюда, через `/plugin marketplace add`. Если эти две копии разойдутся,
# покупатель получит в папке одно, а по строке установки другое, и узнать об этом будет не от кого.
# Ровно такую расхождение build-kit уже ловил у chasecall 25.09.2026 — за сутки на два файла.
#
#   ./sync.sh          — скопировать из рабочих папок сюда
#   ./sync.sh --check  — ничего не менять, упасть, если разошлось (звать перед публикацией)

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
    echo "ПЛОХО: нет рабочей папки $src"
    problems=$((problems + 1))
    continue
  fi
  if [ "$check" -eq 1 ]; then
    # shellcheck disable=SC2086
    diff=$(rsync -rn --delete --itemize-changes $EXCL "$src/" "$HERE/$p/" 2>/dev/null)
    if [ -n "$diff" ]; then
      echo "ПЛОХО: $p здесь разошёлся с $src:"
      echo "$diff" | sed 's/^/    /'
      problems=$((problems + 1))
    else
      echo "  $p — вровень"
    fi
  else
    # shellcheck disable=SC2086
    rsync -a --delete $EXCL "$src/" "$HERE/$p/"
    echo "  $p — скопирован"
  fi
done

# Каждый плагин обязан иметь манифест, иначе Claude Code видит россыпь файлов, а не плагин.
for p in $PLUGINS; do
  [ -s "$HERE/$p/.claude-plugin/plugin.json" ] || {
    echo "ПЛОХО: нет $p/.claude-plugin/plugin.json"; problems=$((problems + 1)); }
done

# И каждый, кто назван в каталоге относительным путём, обязан существовать.
python3 - "$HERE" <<'PY' || problems=$((problems + 1))
import json, sys, os
root = sys.argv[1]
m = json.load(open(os.path.join(root, ".claude-plugin", "marketplace.json"), encoding="utf-8"))
bad = 0
for p in m["plugins"]:
    s = p["source"]
    if isinstance(s, str):
        if not os.path.isdir(os.path.join(root, s)):
            print(f"ПЛОХО: каталог обещает {p['name']} по пути {s}, а папки нет"); bad = 1
    elif s.get("source") == "github" and not s.get("repo"):
        print(f"ПЛОХО: у {p['name']} источник github без repo"); bad = 1
print(f"  каталог: {len(m['plugins'])} плагин(ов), пути проверены")
sys.exit(bad)
PY

echo
if [ "$problems" -eq 0 ]; then
  echo "sync: 0 замечаний"
  exit 0
fi
echo "sync: замечаний — $problems"
exit 1
