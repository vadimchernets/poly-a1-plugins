#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for safecall. Run: python3 -m unittest discover tests

These are written to FAIL if the thing they watch stops working - a check that cannot fail is
decoration. See CONTRIBUTING.md.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "scripts"
SNAP = SCRIPTS / "snapshot.py"
GUARD = SCRIPTS / "guard.py"
STATE = SCRIPTS / "state.py"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="safecall-test-"))
        self.home = self.tmp / "safecall-home"
        self.work = self.tmp / "work"
        self.work.mkdir(parents=True)
        self.env = dict(os.environ, SAFECALL_HOME=str(self.home))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def snap(self, *args):
        return subprocess.run([sys.executable, str(SNAP), *args],
                              capture_output=True, text=True, env=self.env, cwd=str(self.work))

    def guard(self, tool, path, session="conversation-1"):
        """One PreToolUse call. `session` is the conversation, as Claude Code passes it."""
        payload = json.dumps({"tool_name": tool, "session_id": session,
                              "tool_input": {"file_path": str(path)}})
        return subprocess.run([sys.executable, str(GUARD)], input=payload,
                              capture_output=True, text=True, env=self.env, cwd=str(self.work))


class TestSnapshot(Base):
    def test_secret_names_are_refused_in_the_languages_the_person_writes_in(self):
        """A copy of a secret is a second secret - in every language, not only English.

        This guard was English-only until 26.09.2026. The person this plugin is written
        for does not know what a file extension is; they call the file «пароли.txt».
        Found by running it: пароли.txt was copied and nothing was said.
        """
        ordinary = self.work / "письмо.txt"
        ordinary.write_text("обычный файл", encoding="utf-8")

        secrets = ["пароли.txt", "мои-ключи.txt", "паспорт.jpg", "секретное.docx",
                   "senhas.txt", "claves.docx", "contrasenas.txt", "chaves.txt",
                   "passwords.txt", "secret-notes.txt"]
        for name in secrets:
            (self.work / name).write_text("Qwerty!2026", encoding="utf-8")

        paths = [str(ordinary)] + [str(self.work / n) for n in secrets]
        out = self.snap("save", *paths, "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)

        copied = {p.name for p in self.home.rglob("*") if p.is_file()}
        for name in secrets:
            self.assertNotIn(name, copied,
                             "%s was copied — a copy of a secret is a second secret" % name)
        self.assertIn("письмо.txt", copied, "an ordinary file must still be copied")

    def test_save_and_restore_round_trip(self):
        f = self.work / "letter.txt"
        f.write_text("first version", encoding="utf-8")
        self.assertEqual(self.snap("save", str(f), "--folder", str(self.work)).returncode, 0)

        f.write_text("corrupted", encoding="utf-8")
        out = self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(f.read_text(encoding="utf-8"), "first version")

    def test_restore_without_yes_changes_nothing(self):
        f = self.work / "letter.txt"
        f.write_text("original", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        f.write_text("new", encoding="utf-8")

        self.snap("restore", "--folder", str(self.work))
        self.assertEqual(f.read_text(encoding="utf-8"), "new",
                         "without --yes, restore must only show, never touch the file")

    def test_undo_is_itself_undoable(self):
        f = self.work / "letter.txt"
        f.write_text("A", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        f.write_text("B", encoding="utf-8")
        self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(f.read_text(encoding="utf-8"), "A")
        # B must have been copied before being overwritten, so it can come back.
        out = self.snap("list", "--folder", str(self.work))
        self.assertGreaterEqual(out.stdout.count("\n  "), 2,
                                "restore must itself copy what it is about to overwrite")

    def test_secret_named_file_is_never_copied(self):
        for name in (".env", "my-password.txt", "id_rsa", "server.key"):
            with self.subTest(name=name):
                f = self.work / name
                f.write_text("s3cret", encoding="utf-8")
                out = self.snap("save", str(f), "--folder", str(self.work))
                self.assertNotIn("Copy made", out.stdout,
                                 f"{name} was copied, and it should not have been")

    def test_symlink_is_not_copied(self):
        real = self.work / "real.txt"
        real.write_text("x", encoding="utf-8")
        link = self.work / "shortcut.txt"
        link.symlink_to(real)
        out = self.snap("save", str(link), "--folder", str(self.work))
        self.assertNotIn("Copy made", out.stdout)

    def test_covered_says_yes_only_after_a_save(self):
        f = self.work / "letter.txt"
        f.write_text("x", encoding="utf-8")
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 1)
        self.snap("save", str(f), "--folder", str(self.work))
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 0)

    # ── Legacy snapshots (safecall <= 0.1.0, before the Russian->English rename) ────────────
    #
    # `снимок.json` and its Russian keys were renamed to `snapshot.json` / English keys. A
    # person who already has copies made by the old version must not lose them on upgrade:
    # list, restore and covered must still read a snapshot in the old shape. New snapshots are
    # always written in the new shape - only reading looks back.

    def _make_legacy_snapshot(self, *files):
        """Make one real snapshot (so the directory/slug are exactly what the real code would
        use), then rewrite its metadata file into the pre-rename shape: `снимок.json` with
        Russian keys, in place of `snapshot.json`."""
        out = self.snap("save", *[str(f) for f in files], "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        slug_dirs = [d for d in (self.home / "copies").iterdir() if d.is_dir()]
        self.assertEqual(len(slug_dirs), 1, "expected exactly one work-folder slug directory")
        shot_dirs = [d for d in slug_dirs[0].iterdir() if d.is_dir()]
        self.assertEqual(len(shot_dirs), 1, "expected exactly one snapshot directory")
        shot_dir = shot_dirs[0]
        meta = json.loads((shot_dir / "snapshot.json").read_text(encoding="utf-8"))
        legacy = {
            "когда": meta["when"], "папка": meta["folder"],
            "файлы": [{"файл": e["file"], "внутри": e["inside"], "байт": e["bytes"]}
                      for e in meta["files"]],
            "пропущено": meta["skipped"],
        }
        (shot_dir / "снимок.json").write_text(json.dumps(legacy, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
        (shot_dir / "snapshot.json").unlink()
        return shot_dir

    def test_legacy_snapshot_is_listed_covered_and_restorable(self):
        """A copy made by the pre-rename version must still work end to end after upgrading."""
        f = self.work / "letter.txt"
        f.write_text("first version", encoding="utf-8")
        self._make_legacy_snapshot(f)

        out = self.snap("list", "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("letter.txt", out.stdout, "a legacy snapshot must appear in the list")

        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 0,
                         "a legacy snapshot must count as covering the file")

        f.write_text("corrupted", encoding="utf-8")
        out = self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(f.read_text(encoding="utf-8"), "first version",
                         "restore must work from a legacy snapshot")

    def test_restore_of_an_old_snapshot_does_not_delete_it_first(self):
        """Pre-existing bug, found while adding legacy reading (not specific to the rename):
        `restore` backs up the current state before overwriting, and that backup save used to
        prune the ENTIRE folder of old/excess snapshots - including the one `restore` was in
        the middle of reading from, if it happened to be older than the 14-day keep window.
        That made restoring an old copy silently restore nothing ("Restored 0 file(s)").
        """
        f = self.work / "letter.txt"
        f.write_text("first version", encoding="utf-8")
        shot_dir = self._make_legacy_snapshot(f)

        # Backdate the snapshot well past KEEP_DAYS (14), the way a snapshot genuinely made
        # before an upgrade would be by the time somebody gets around to restoring it.
        old_name = "2020-01-01_00-00-00"
        old_dir = shot_dir.parent / old_name
        shot_dir.rename(old_dir)
        legacy_meta = json.loads((old_dir / "снимок.json").read_text(encoding="utf-8"))
        legacy_meta["когда"] = old_name
        (old_dir / "снимок.json").write_text(json.dumps(legacy_meta, ensure_ascii=False, indent=2),
                                             encoding="utf-8")

        f.write_text("corrupted", encoding="utf-8")
        out = self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(f.read_text(encoding="utf-8"), "first version",
                         "restoring an old snapshot must not delete it before reading it")
        self.assertTrue(old_dir.exists(), "the snapshot just restored from must survive the restore")


class TestGuard(Base):
    def test_makes_the_copy_itself_and_allows(self):
        """The main promise: the edit goes through, and a copy already exists by then.

        The first version blocked instead and printed the person a command. The round of
        criticism killed that design with two scenarios: Poly A1's own coach appends to a state
        file every evening, and from the second evening on the guard was stopping exactly the
        action that ends an evening well.
        """
        f = self.work / "contract.txt"
        f.write_text("important", encoding="utf-8")
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 0,
                         "the edit must not be blocked: the guard makes the copy itself")
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 0,
                         "a copy must exist after the hook runs")

    def test_never_stops_the_evening_note(self):
        """The state file the coach appends to every evening must never meet a block."""
        for name in ("NEXT.md", "СЕЙЧАС.md", "ЗАРАЗ.md", "AHORA.md", "AGORA.md"):
            with self.subTest(name=name):
                f = self.work / name
                f.write_text("yesterday's content", encoding="utf-8")
                self.assertEqual(self.guard("Edit", f).returncode, 0)

    def test_allows_a_brand_new_file(self):
        out = self.guard("Write", self.work / "does-not-exist-yet.txt")
        self.assertEqual(out.returncode, 0, "a new file has nothing to lose — must not be blocked")

    def test_allows_when_a_copy_already_exists(self):
        f = self.work / "contract.txt"
        f.write_text("important", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        self.assertEqual(self.guard("Write", f).returncode, 0)

    def test_blocks_only_what_cannot_be_copied(self):
        """The one case for refusal: the copy could not be made, so the edit would be one-way."""
        f = self.work / "server.key"          # name says "key" — copying this is refused on purpose
        f.write_text("secret", encoding="utf-8")
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 2)
        self.assertIn("could not copy", out.stderr)

    def test_refusal_message_is_in_english(self):
        """The script's own refusal text is English by default; the skill that calls it is the
        one that tells Claude to relay it in the person's own language.
        """
        f = self.work / "server.key"
        f.write_text("secret", encoding="utf-8")
        err = self.guard("Write", f).stderr
        self.assertIn("could not copy", err)
        self.assertIn("THEIR language", err,
                      "the message must tell Claude to relay this in the person's own language")

    # ── The pass: how long "yes, change it without a copy" lasts ────────────────────────────
    #
    # There used to be one test here - `test_second_attempt_passes_after_the_person_was_asked`.
    # It took `server.key` (a name that is NEVER copied, on purpose) and pinned down that the
    # second attempt goes through. It checked something true, but it hid a far more important
    # lie: the same permanent pass was also given to an ordinary document whose copy failed ONCE,
    # by accident. The decision of the council of AIs on 26.09.2026 was: fix it, and split it.
    # The four tests below are each written so they can go red, and each one says in itself what
    # makes it go red.

    def test_one_failed_copy_does_not_disable_copies(self):
        """A copy failed once — the file must be protected again as soon as it can be.

        Goes red on the code before 26.09.2026: there, the path went into `uncopyable.txt`
        forever, and the third attempt skipped the copy silently - "copied" never appeared in
        the reply.
        """
        f = self.work / "contract.txt"
        f.write_bytes(b"x" * (6 * 1024 * 1024))       # over 5 MB — cannot be copied
        self.assertEqual(self.guard("Write", f).returncode, 2, "no copy exists — must stop")
        self.assertEqual(self.guard("Write", f).returncode, 0,
                         "the person was asked — now let it through")

        f.write_text("now small", encoding="utf-8")    # the reason for the failure is gone
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 0)
        self.assertIn(f'copied "{f.name}"', out.stdout,
                      "the reason for the failure is gone — the guard must copy again, not stay silent")

    def test_secret_pass_lasts_the_conversation(self):
        """A secret is never copied, so its pass lasts the whole conversation.

        Goes red if the pass is made one-shot: the third attempt would then return 2.
        """
        f = self.work / "server.key"
        f.write_text("secret", encoding="utf-8")
        self.assertEqual(self.guard("Write", f).returncode, 2)
        self.assertEqual(self.guard("Write", f).returncode, 0)
        self.assertEqual(self.guard("Write", f).returncode, 0,
                         "the person was asked once — must not be asked again in the same conversation")

    def test_pass_does_not_cross_conversations(self):
        """A new conversation asks again: whoever answered before may not be who is sitting
        there now.

        Goes red on the code before 26.09.2026, and on any version where the pass is keyed by
        path alone.
        """
        f = self.work / "server.key"
        f.write_text("secret", encoding="utf-8")
        self.assertEqual(self.guard("Write", f, session="conversation-A").returncode, 2)
        self.assertEqual(self.guard("Write", f, session="conversation-A").returncode, 0)
        self.assertEqual(self.guard("Write", f, session="conversation-B").returncode, 2,
                         "this other conversation was never asked — it must be asked")

    def test_guard_never_blocks_forever_when_its_own_home_is_broken(self):
        """Its own home folder is unreachable — the guard lets the edit through and says so,
        instead of locking the work forever.

        Without this, one disk failure would stop EVERY edit: no copy can be made, nowhere to
        write the pass, and repeating the edit does not help. The "fail open" rule is in
        guard.py's header. Goes red if a block is brought back when writing the pass fails.
        """
        broken = self.tmp / "not-a-folder"
        broken.write_text("I am a file, not a folder", encoding="utf-8")
        env = dict(os.environ, SAFECALL_HOME=str(broken))
        f = self.work / "contract.txt"
        f.write_text("important", encoding="utf-8")
        payload = json.dumps({"tool_name": "Write", "session_id": "conversation-1",
                              "tool_input": {"file_path": str(f)}})
        out = subprocess.run([sys.executable, str(GUARD)], input=payload,
                             capture_output=True, text=True, env=env, cwd=str(self.work))
        self.assertEqual(out.returncode, 0, "the guard has no right to lock the work forever")
        self.assertIn("WITH NO COPY", out.stdout, "it went through with no copy — the person is told")

    def test_never_blocks_reading(self):
        f = self.work / "contract.txt"
        f.write_text("important", encoding="utf-8")
        for tool in ("Read", "Grep", "Glob", "Bash"):
            with self.subTest(tool=tool):
                self.assertEqual(self.guard(tool, f).returncode, 0)

    def test_fails_open_on_unreadable_input(self):
        out = subprocess.run([sys.executable, str(GUARD)], input="not json",
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0, "the guard has no right to break the session")


class TestState(Base):
    def test_now_prints_a_real_year(self):
        from datetime import datetime
        out = subprocess.run([sys.executable, str(STATE), "now"],
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0)
        self.assertIn(str(datetime.now().year), out.stdout)

    def test_note_round_trip(self):
        subprocess.run([sys.executable, str(STATE), "save", "--folder", str(self.work),
                        "--done", "read the contract", "--next", "write the reply"],
                       capture_output=True, text=True, env=self.env)
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertIn("read the contract", out.stdout)
        self.assertIn("write the reply", out.stdout)

    def test_no_note_says_first_time(self):
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertIn("first time", out.stdout)

    # ── Legacy notes (safecall <= 0.1.0, before the Russian->English rename) ────────────────
    #
    # `где-остановились/` and its Russian keys were renamed to `notes/` / English keys. A
    # person who already has a "where we stopped" note from the old version must still see it.

    def _make_legacy_note(self, **fields):
        """Write one real note (so the file name - folder slug plus hash - is exactly what the
        real code would use), then move it into the pre-rename location with Russian keys."""
        args = [sys.executable, str(STATE), "save", "--folder", str(self.work)]
        for k, v in fields.items():
            args += [f"--{k}", v]
        out = subprocess.run(args, capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0, out.stderr)
        notes = list((self.home / "notes").iterdir())
        self.assertEqual(len(notes), 1, "expected exactly one note file")
        note_path = notes[0]
        data = json.loads(note_path.read_text(encoding="utf-8"))
        legacy = {"когда": data["when"], "папка": data["folder"], "сделано": data["done"],
                  "не_сделано": data["left"], "дальше": data["next"], "ловушки": data["traps"]}
        legacy_dir = self.home / "где-остановились"
        legacy_dir.mkdir(parents=True, exist_ok=True)
        (legacy_dir / note_path.name).write_text(
            json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8")
        note_path.unlink()
        return legacy_dir / note_path.name

    def test_legacy_note_is_shown_when_no_new_note_exists(self):
        self._make_legacy_note(done="read the contract", left="send it",
                               next="attach the receipt", traps="the deadline is Friday")
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn("read the contract", out.stdout)
        self.assertIn("send it", out.stdout)
        self.assertIn("attach the receipt", out.stdout)
        self.assertIn("the deadline is Friday", out.stdout)

    def test_new_note_is_preferred_over_a_legacy_one(self):
        self._make_legacy_note(done="old legacy work", left="old left", next="old next")
        subprocess.run([sys.executable, str(STATE), "save", "--folder", str(self.work),
                        "--done", "new current work", "--next", "new next"],
                       capture_output=True, text=True, env=self.env)
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertIn("new current work", out.stdout)
        self.assertNotIn("old legacy work", out.stdout,
                         "a current note must win over a legacy one for the same folder")


class TestNamedFiles(Base):
    """A file named in an answer must actually exist. This checks the claim against the disk."""

    def paths(self, text, folder=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "paths.py"), "--folder", str(folder or self.work),
             "--text", text],
            capture_output=True, text=True, env=self.env)

    def test_existing_file_passes(self):
        (self.work / "contract.pdf").write_text("x", encoding="utf-8")
        out = self.paths("I read contract.pdf, and everything there is in order.")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("exists: contract.pdf", out.stdout)

    def test_invented_file_is_caught(self):
        (self.work / "contract.pdf").write_text("x", encoding="utf-8")
        out = self.paths("There is a contract-2024.pdf in your folder, and it says…")
        self.assertEqual(out.returncode, 1, "an invented file must be caught")
        self.assertIn("MISSING: contract-2024.pdf", out.stdout)

    def test_file_one_folder_down_is_found_not_denied(self):
        """The file exists, just deeper. Saying "there is no such file" is also a wrong answer."""
        sub = self.work / "Documents"
        sub.mkdir()
        (sub / "invoice.pdf").write_text("x", encoding="utf-8")
        out = self.paths("Take a look at invoice.pdf")
        self.assertEqual(out.returncode, 0)
        self.assertIn("Documents", out.stdout)

    def test_urls_and_versions_are_not_files(self):
        out = self.paths("Open https://polyhelper.ai/en.zip, version 2.1.283, those are not files.")
        self.assertNotIn("MISSING: https", out.stdout)
        self.assertNotIn("MISSING: 2.1.283", out.stdout)

    def test_text_with_no_filenames_says_so(self):
        out = self.paths("Just an answer with no file name in it at all.")
        self.assertEqual(out.returncode, 0)
        self.assertIn("No file was named", out.stdout)

    def test_quoted_names_are_seen(self):
        (self.work / "letter.txt").write_text("x", encoding="utf-8")
        out = self.paths('I opened "letter.txt" and read it.')
        self.assertIn("exists: letter.txt", out.stdout)


if __name__ == "__main__":
    unittest.main()
