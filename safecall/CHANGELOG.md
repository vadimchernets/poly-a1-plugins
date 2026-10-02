# Changelog

## 0.1.1 — 2026-10-02

- Project language is English: comments, skill instructions, script output and docs translated; skills
  answer in the person's language. Russian stays only as a localization (README.ru.md, the ru/uk entries
  of the secret-name word list, ru test fixtures).
- Runtime names are English now (`snapshot.json` and its keys, the `notes/` folder for "where we stopped",
  `README.txt` in `~/.safecall`). Copies and notes made by 0.1.0 under the old Russian names are still
  read: listed, restored, checked by `covered`, shown as last time's note. Nothing on disk is renamed.
- Fix: restoring an old snapshot could prune that very snapshot before copying out of it.
- The Russian-scenario behaviour suite now lives in `tests/behavior/ru/` as the Russian localization of
  the suite; `run.py --lang` picks a language (default: every language folder present). One checker
  pattern widened so a correct refusal phrased with words in between is no longer marked as a failure.
