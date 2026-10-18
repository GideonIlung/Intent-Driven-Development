import unittest
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


if __name__ == "__main__":
    unittest.main()
