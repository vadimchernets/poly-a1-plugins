# Changelog

## 0.1.2 — 2026-10-02

- Every language is equal now: the per-language word tables (the Poly A1 coach's state-file name,
  the secret-name word list) moved out of `scripts/guard.py` and `scripts/snapshot.py` into their
  own `lang/<code>.json` file - one file per language (`en`, `es`, `pt`, `ru`, `uk`), read the same
  way, none of them hardcoded into the Python source as a special case of another. Behaviour is
  unchanged: the same files are still refused, the same state-file names are still never blocked.
- Ukrainian's secret-name words are no longer a lightly-adapted copy of the Russian ones: its own
  spellings of "login" and "PIN code" (distinct from the Russian ones - see `lang/uk.json`) are
  matched alongside the words the two languages do share. Spanish and Portuguese gained
  `pasaporte`/`passaporte` and a safely word-bounded `pin`, so a passport or a PIN code is caught
  in those languages too, not only `.env` and `id_rsa`.
- The old (safecall <= 0.1.0) Russian metadata and note names - the legacy snapshot meta file and
  its keys, the legacy "where we stopped" notes folder and its keys - moved into lang/ru.json's
  `"legacy"` section. `scripts/snapshot.py` and `scripts/state.py` read them from there; reading an
  old copy or note made before the 0.1.0->0.1.1 rename still works exactly as before.
- Added `scripts/check_language.py` (`python3 scripts/check_language.py`): fails if Cyrillic
  appears anywhere outside a language place (a `ru`/`uk` path segment, `README.ru.md`,
  `lang/ru.json`, `lang/uk.json`, or a language's own self-name in a list of languages). Every
  Russian or Ukrainian literal that used to live in `scripts/guard.py`, `scripts/snapshot.py`,
  `scripts/state.py`, `tests/test_safecall.py` and `tests/behavior/run.py` moved into `lang/*.json`
  or `tests/fixtures/ru|uk/` to pass it; the checker itself is covered by
  `tests/test_check_language.py`.
- Tests: added coverage that every `lang/<code>.json` loads and has the shared shape, that one
  natural secret-named sample file per language (en/es/pt/ru/uk) is refused, and that the legacy
  Russian names are still read correctly - alongside the existing round-trip and legacy tests,
  which keep their original assertions unchanged.
- Two stray bytecode files (`tests/__pycache__/*.pyc`) are no longer tracked.

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
