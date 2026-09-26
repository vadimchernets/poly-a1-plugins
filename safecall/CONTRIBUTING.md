# Contributing

The person this plugin is written for is sixty, is not a programmer, and has one folder of
documents that matters to them. Every change is judged by what it does for them.

- **No dependencies.** Python 3.8+ and the standard library. A plugin that needs `pip install`
  has already lost this person.
- **No network.** Not for telemetry, not for updates, not for anything.
- **Plain words in anything a person sees.** Not "repository", "commit", "directory", "backup" —
  "папка", "копия", "файл". English error text is translated, never repeated at them.
- **A guard that can fail open, fails open.** Breaking somebody's session is worse than missing one
  snapshot.
- **Run the tests:** `python3 -m pytest tests/ -q` (or `python3 -m unittest discover tests`).
- **Break your own guard before you trust it.** Add a check, then deliberately break the thing it
  watches and confirm it goes red; put it back and confirm it goes green. A check that cannot fail
  is decoration.
