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
        self.work = self.tmp / "работа"
        self.work.mkdir(parents=True)
        self.env = dict(os.environ, SAFECALL_HOME=str(self.home))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def snap(self, *args):
        return subprocess.run([sys.executable, str(SNAP), *args],
                              capture_output=True, text=True, env=self.env, cwd=str(self.work))

    def guard(self, tool, path, session="разговор-1"):
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
                             "%s скопирован — копия секрета это второй секрет" % name)
        self.assertIn("письмо.txt", copied, "обычный файл копировать всё равно надо")

    def test_save_and_restore_round_trip(self):
        f = self.work / "письмо.txt"
        f.write_text("первая версия", encoding="utf-8")
        self.assertEqual(self.snap("save", str(f), "--folder", str(self.work)).returncode, 0)

        f.write_text("испорчено", encoding="utf-8")
        out = self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(f.read_text(encoding="utf-8"), "первая версия")

    def test_restore_without_yes_changes_nothing(self):
        f = self.work / "письмо.txt"
        f.write_text("оригинал", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        f.write_text("новое", encoding="utf-8")

        self.snap("restore", "--folder", str(self.work))
        self.assertEqual(f.read_text(encoding="utf-8"), "новое",
                         "без --yes restore обязан только показать, но не трогать файл")

    def test_undo_is_itself_undoable(self):
        f = self.work / "письмо.txt"
        f.write_text("A", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        f.write_text("B", encoding="utf-8")
        self.snap("restore", "--yes", "--folder", str(self.work))
        self.assertEqual(f.read_text(encoding="utf-8"), "A")
        # B must have been copied before being overwritten, so it can come back.
        out = self.snap("list", "--folder", str(self.work))
        self.assertGreaterEqual(out.stdout.count("\n  "), 2,
                                "возврат обязан сам сделать копию того, что затирает")

    def test_secret_named_file_is_never_copied(self):
        for name in (".env", "my-password.txt", "id_rsa", "server.key"):
            with self.subTest(name=name):
                f = self.work / name
                f.write_text("s3cret", encoding="utf-8")
                out = self.snap("save", str(f), "--folder", str(self.work))
                self.assertNotIn("Копия сделана", out.stdout,
                                 f"{name} скопирован, а не должен")

    def test_symlink_is_not_copied(self):
        real = self.work / "настоящий.txt"
        real.write_text("x", encoding="utf-8")
        link = self.work / "ярлык.txt"
        link.symlink_to(real)
        out = self.snap("save", str(link), "--folder", str(self.work))
        self.assertNotIn("Копия сделана", out.stdout)

    def test_covered_says_yes_only_after_a_save(self):
        f = self.work / "письмо.txt"
        f.write_text("x", encoding="utf-8")
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 1)
        self.snap("save", str(f), "--folder", str(self.work))
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 0)


class TestGuard(Base):
    def test_makes_the_copy_itself_and_allows(self):
        """Главное обещание: правка проходит, и копия к этому моменту уже есть.

        Первая версия вместо этого блокировала и печатала человеку команду. Круг критики убил тот
        замысел двумя сценариями: коуч Poly A1 каждый вечер дописывает файл состояния, и со второго
        вечера сторож останавливал ровно то действие, которым вечер хорошо кончается.
        """
        f = self.work / "договор.txt"
        f.write_text("важное", encoding="utf-8")
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 0, "правка не должна стопориться: копию сторож делает сам")
        self.assertEqual(self.snap("covered", str(f), "--folder", str(self.work)).returncode, 0,
                         "после хука копия обязана существовать")

    def test_never_stops_the_evening_note(self):
        """Файл состояния, который коуч дописывает каждый вечер, не должен встречать преграду."""
        for name in ("NEXT.md", "СЕЙЧАС.md", "ЗАРАЗ.md", "AHORA.md", "AGORA.md"):
            with self.subTest(name=name):
                f = self.work / name
                f.write_text("вчерашнее", encoding="utf-8")
                self.assertEqual(self.guard("Edit", f).returncode, 0)

    def test_allows_a_brand_new_file(self):
        out = self.guard("Write", self.work / "которого-ещё-нет.txt")
        self.assertEqual(out.returncode, 0, "новый файл терять нечего — блокировать нельзя")

    def test_allows_when_a_copy_already_exists(self):
        f = self.work / "договор.txt"
        f.write_text("важное", encoding="utf-8")
        self.snap("save", str(f), "--folder", str(self.work))
        self.assertEqual(self.guard("Write", f).returncode, 0)

    def test_blocks_only_what_cannot_be_copied(self):
        """Единственный случай отказа: копию сделать нельзя, значит правка была бы без возврата."""
        f = self.work / "server.key"          # имя про ключ — копировать такое запрещено нарочно
        f.write_text("секрет", encoding="utf-8")
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 2)
        self.assertIn("could not copy", out.stderr)

    def test_refusal_is_bilingual(self):
        f = self.work / "server.key"
        f.write_text("секрет", encoding="utf-8")
        err = self.guard("Write", f).stderr
        self.assertIn("не смог сделать копию", err)
        self.assertIn("could not copy", err,
                      "покупателей пять языков — отказ не может быть только по-русски")

    # ── Пропуск: сколько живёт «да, меняйте без копии» ───────────────────────────────────
    #
    # Здесь стоял один тест — `test_second_attempt_passes_after_the_person_was_asked`. Он брал
    # `server.key` (такое имя не копируется НАРОЧНО и навсегда) и закреплял, что второй заход
    # проходит. Проверял он правду, но закрывал собой куда более важную ложь: тот же вечный
    # пропуск получал и обычный документ, у которого копия сорвалась ОДИН раз случайно. Решение
    # совета ИИ 26.09.2026 — чинить и разделить. Четыре теста ниже написаны так, чтобы каждый
    # умел покраснеть, и чем именно он краснеет — сказано в нём самом.

    def test_one_failed_copy_does_not_disable_copies(self):
        """Сорвалась копия один раз — файл обязан защищаться снова, как только сможет.

        Краснеет на коде до 26.09.2026: там путь попадал в `uncopyable.txt` навсегда, и третий
        заход уходил мимо копии молча — «сделал копию» в ответе не появлялось.
        """
        f = self.work / "договор.txt"
        f.write_bytes(b"x" * (6 * 1024 * 1024))       # больше 5 МБ — скопировать нельзя
        self.assertEqual(self.guard("Write", f).returncode, 2, "копии нет — надо остановить")
        self.assertEqual(self.guard("Write", f).returncode, 0, "человека спросили — пропускаем")

        f.write_text("теперь маленький", encoding="utf-8")   # причина сбоя ушла
        out = self.guard("Write", f)
        self.assertEqual(out.returncode, 0)
        self.assertIn("сделал копию", out.stdout,
                      "причина сбоя ушла — сторож обязан снова делать копию, а не молчать")

    def test_secret_pass_lasts_the_conversation(self):
        """Секрет не копируется никогда, поэтому его пропуск держится весь разговор.

        Краснеет, если сделать пропуск одноразовым: третий заход вернёт 2.
        """
        f = self.work / "server.key"
        f.write_text("секрет", encoding="utf-8")
        self.assertEqual(self.guard("Write", f).returncode, 2)
        self.assertEqual(self.guard("Write", f).returncode, 0)
        self.assertEqual(self.guard("Write", f).returncode, 0,
                         "человека спросили один раз — переспрашивать в том же разговоре нельзя")

    def test_pass_does_not_cross_conversations(self):
        """Новый разговор спрашивает заново: отвечал, возможно, не тот, кто сидит сейчас.

        Краснеет на коде до 26.09.2026 и на любом, где пропуск хранится по одному лишь пути.
        """
        f = self.work / "server.key"
        f.write_text("секрет", encoding="utf-8")
        self.assertEqual(self.guard("Write", f, session="разговор-A").returncode, 2)
        self.assertEqual(self.guard("Write", f, session="разговор-A").returncode, 0)
        self.assertEqual(self.guard("Write", f, session="разговор-Б").returncode, 2,
                         "в другом разговоре человека не спрашивали — надо спросить")

    def test_guard_never_blocks_forever_when_its_own_home_is_broken(self):
        """Своя папка недоступна — сторож пропускает и говорит, а не запирает работу навсегда.

        Без этого один сбой диска останавливал бы КАЖДУЮ правку: копию сделать нельзя, пропуск
        записать некуда, и повтор правки не помогает. Правило «падать открытым» — в шапке guard.py.
        Краснеет, если вернуть блокировку при неудачной записи пропуска.
        """
        broken = self.tmp / "не-папка"
        broken.write_text("я файл, а не папка", encoding="utf-8")
        env = dict(os.environ, SAFECALL_HOME=str(broken))
        f = self.work / "договор.txt"
        f.write_text("важное", encoding="utf-8")
        payload = json.dumps({"tool_name": "Write", "session_id": "разговор-1",
                              "tool_input": {"file_path": str(f)}})
        out = subprocess.run([sys.executable, str(GUARD)], input=payload,
                             capture_output=True, text=True, env=env, cwd=str(self.work))
        self.assertEqual(out.returncode, 0, "сторож не имеет права запереть работу навсегда")
        self.assertIn("БЕЗ копии", out.stdout, "прошло без копии — человеку об этом говорят")

    def test_never_blocks_reading(self):
        f = self.work / "договор.txt"
        f.write_text("важное", encoding="utf-8")
        for tool in ("Read", "Grep", "Glob", "Bash"):
            with self.subTest(tool=tool):
                self.assertEqual(self.guard(tool, f).returncode, 0)

    def test_fails_open_on_unreadable_input(self):
        out = subprocess.run([sys.executable, str(GUARD)], input="не json",
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0, "сторож не имеет права ломать сессию")


class TestState(Base):
    def test_now_prints_a_real_year(self):
        from datetime import datetime
        out = subprocess.run([sys.executable, str(STATE), "now"],
                             capture_output=True, text=True, env=self.env)
        self.assertEqual(out.returncode, 0)
        self.assertIn(str(datetime.now().year), out.stdout)

    def test_note_round_trip(self):
        subprocess.run([sys.executable, str(STATE), "save", "--folder", str(self.work),
                        "--done", "прочитали договор", "--next", "написать ответ"],
                       capture_output=True, text=True, env=self.env)
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertIn("прочитали договор", out.stdout)
        self.assertIn("написать ответ", out.stdout)

    def test_no_note_says_first_time(self):
        out = subprocess.run([sys.executable, str(STATE), "show", "--folder", str(self.work)],
                             capture_output=True, text=True, env=self.env)
        self.assertIn("первый раз", out.stdout)


class TestNamedFiles(Base):
    """Файл, названный в ответе, обязан существовать. Это проверка утверждения о диске."""

    def paths(self, text, folder=None):
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "paths.py"), "--folder", str(folder or self.work),
             "--text", text],
            capture_output=True, text=True, env=self.env)

    def test_existing_file_passes(self):
        (self.work / "договор.pdf").write_text("x", encoding="utf-8")
        out = self.paths("Я прочитал договор.pdf, там всё в порядке.")
        self.assertEqual(out.returncode, 0, out.stdout)
        self.assertIn("есть: договор.pdf", out.stdout)

    def test_invented_file_is_caught(self):
        (self.work / "договор.pdf").write_text("x", encoding="utf-8")
        out = self.paths("В вашей папке есть договор-2024.pdf, в нём сказано…")
        self.assertEqual(out.returncode, 1, "выдуманный файл обязан ловиться")
        self.assertIn("НЕТ: договор-2024.pdf", out.stdout)

    def test_file_one_folder_down_is_found_not_denied(self):
        """Файл есть, но глубже. Сказать «такого нет» — тоже неверный ответ."""
        sub = self.work / "Документы"
        sub.mkdir()
        (sub / "счёт.pdf").write_text("x", encoding="utf-8")
        out = self.paths("Посмотрите счёт.pdf")
        self.assertEqual(out.returncode, 0)
        self.assertIn("Документы", out.stdout)

    def test_urls_and_versions_are_not_files(self):
        out = self.paths("Откройте https://polyhelper.ai/ru.zip, версия 2.1.283, это не файлы.")
        self.assertNotIn("НЕТ: https", out.stdout)
        self.assertNotIn("НЕТ: 2.1.283", out.stdout)

    def test_text_with_no_filenames_says_so(self):
        out = self.paths("Просто ответ без единого имени файла.")
        self.assertEqual(out.returncode, 0)
        self.assertIn("не названо ни одного файла", out.stdout)

    def test_quoted_names_are_seen(self):
        (self.work / "письмо.txt").write_text("x", encoding="utf-8")
        out = self.paths("Я открыл «письмо.txt» и прочитал.")
        self.assertIn("есть: письмо.txt", out.stdout)


if __name__ == "__main__":
    unittest.main()
