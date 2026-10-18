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


if __name__ == "__main__":
    unittest.main()
