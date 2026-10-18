import unittest
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from todo import cli


class CommandTests(unittest.TestCase):
    @patch("todo.cli.tasks.add")
    def test_add_parses_title(self, add):
        self.assertEqual(cli.main(["add", "Buy milk"]), 0)
        add.assert_called_once_with("Buy milk")

    @patch("todo.cli.tasks.list_outstanding")
    def test_list_defaults_to_outstanding(self, list_outstanding):
        self.assertEqual(cli.main(["list"]), 0)
        list_outstanding.assert_called_once_with()

    @patch("todo.cli.tasks.list_all")
    def test_list_all_parses_flag(self, list_all):
        self.assertEqual(cli.main(["list", "--all"]), 0)
        list_all.assert_called_once_with()

    @patch("todo.cli.tasks.complete")
    def test_complete_parses_identifier(self, complete):
        self.assertEqual(cli.main(["complete", "12"]), 0)
        complete.assert_called_once_with(12)

    @patch("todo.cli.tasks.edit")
    def test_edit_parses_identifier_and_title(self, edit):
        self.assertEqual(cli.main(["edit", "12", "Buy bread"]), 0)
        edit.assert_called_once_with(12, "Buy bread")

    @patch("todo.cli.tasks.delete")
    def test_delete_parses_identifier(self, delete):
        self.assertEqual(cli.main(["delete", "12"]), 0)
        delete.assert_called_once_with(12)


class StorageTests(unittest.TestCase):
    def test_task_persists_across_command_runs(self):
        with tempfile.TemporaryDirectory() as home:
            environment = os.environ.copy()
            environment["HOME"] = home
            source = str(Path(__file__).parents[1] / "src")
            environment["PYTHONPATH"] = source

            added = subprocess.run(
                [sys.executable, "-m", "todo", "add", "Buy milk"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            listed = subprocess.run(
                [sys.executable, "-m", "todo", "list"],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(added.returncode, 0, added.stderr)
            self.assertIn("1", added.stdout)
            self.assertEqual(listed.returncode, 0, listed.stderr)
            self.assertIn("Buy milk", listed.stdout)

            saved = json.loads(
                (Path(home) / ".todo" / "tasks.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                saved,
                {
                    "tasks": [
                        {"id": 1, "text": "Buy milk", "completed": False}
                    ]
                },
            )

    def test_malformed_data_is_reported_without_overwriting(self):
        with tempfile.TemporaryDirectory() as home:
            task_file = Path(home) / ".todo" / "tasks.json"
            task_file.parent.mkdir()
            malformed = "not json\n"
            task_file.write_text(malformed, encoding="utf-8")

            with patch.dict(os.environ, {"HOME": home}):
                result = cli.main(["add", "Buy milk"])

            self.assertEqual(result, 1)
            self.assertEqual(task_file.read_text(encoding="utf-8"), malformed)


class TaskOperationTests(unittest.TestCase):
    def setUp(self):
        self.temporary_home = tempfile.TemporaryDirectory()
        self.home = self.temporary_home.name
        self.environment = os.environ.copy()
        self.environment["HOME"] = self.home
        self.environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")

    def tearDown(self):
        self.temporary_home.cleanup()

    def run_todo(self, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "todo", *arguments],
            env=self.environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def saved_tasks(self):
        task_file = Path(self.home) / ".todo" / "tasks.json"
        return json.loads(task_file.read_text(encoding="utf-8"))["tasks"]

    def test_list_filters_completed_tasks_unless_all_requested(self):
        self.run_todo("add", "Buy milk")
        self.run_todo("add", "Wash car")
        self.run_todo("complete", "2")

        outstanding = self.run_todo("list")
        all_tasks = self.run_todo("list", "--all")

        self.assertEqual(outstanding.returncode, 0, outstanding.stderr)
        self.assertIn("Buy milk", outstanding.stdout)
        self.assertNotIn("Wash car", outstanding.stdout)
        self.assertEqual(all_tasks.returncode, 0, all_tasks.stderr)
        self.assertIn("Buy milk", all_tasks.stdout)
        self.assertIn("Wash car [completed]", all_tasks.stdout)

    def test_complete_persists_and_hides_task(self):
        self.run_todo("add", "Buy milk")

        completed = self.run_todo("complete", "1")
        listed = self.run_todo("list")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue(self.saved_tasks()[0]["completed"])
        self.assertNotIn("Buy milk", listed.stdout)

    def test_edit_persists_new_text(self):
        self.run_todo("add", "Buy milk")

        edited = self.run_todo("edit", "1", "Buy bread")

        self.assertEqual(edited.returncode, 0, edited.stderr)
        self.assertEqual(self.saved_tasks()[0]["text"], "Buy bread")

    def test_delete_removes_task_from_all_lists(self):
        self.run_todo("add", "Buy milk")

        deleted = self.run_todo("delete", "1")
        listed = self.run_todo("list", "--all")

        self.assertEqual(deleted.returncode, 0, deleted.stderr)
        self.assertEqual(self.saved_tasks(), [])
        self.assertNotIn("Buy milk", listed.stdout)

    def test_unknown_identifiers_are_reported_without_changes(self):
        commands = [
            ("complete", "2"),
            ("edit", "2", "Buy bread"),
            ("delete", "2"),
        ]
        for command in commands:
            with self.subTest(command=command):
                if not self.saved_task_file_exists():
                    self.run_todo("add", "Buy milk")
                before = self.saved_tasks()

                result = self.run_todo(*command)

                self.assertEqual(result.returncode, 1)
                self.assertIn("task 2 does not exist", result.stderr)
                self.assertEqual(self.saved_tasks(), before)

    def saved_task_file_exists(self):
        return (Path(self.home) / ".todo" / "tasks.json").exists()


if __name__ == "__main__":
    unittest.main()
