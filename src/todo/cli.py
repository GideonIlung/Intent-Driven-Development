"""Command-line interface for the local task manager."""

import argparse
from typing import Optional, Sequence

from todo import tasks


def add(title: str) -> None:
    tasks.add(title)


def list_tasks(show_all: bool = False) -> None:
    if show_all:
        tasks.list_all()
    else:
        tasks.list_outstanding()


def complete(task_id: int) -> None:
    tasks.complete(task_id)


def edit(task_id: int, title: str) -> None:
    tasks.edit(task_id, title)


def delete(task_id: int) -> None:
    tasks.delete(task_id)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="todo")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="add a task")
    add_parser.add_argument("title")
    add_parser.set_defaults(handler=lambda args: add(args.title))

    list_parser = commands.add_parser("list", help="list tasks")
    list_parser.add_argument("--all", action="store_true", dest="show_all")
    list_parser.set_defaults(handler=lambda args: list_tasks(args.show_all))

    complete_parser = commands.add_parser("complete", help="complete a task")
    complete_parser.add_argument("task_id", type=int)
    complete_parser.set_defaults(handler=lambda args: complete(args.task_id))

    edit_parser = commands.add_parser("edit", help="edit a task")
    edit_parser.add_argument("task_id", type=int)
    edit_parser.add_argument("title")
    edit_parser.set_defaults(handler=lambda args: edit(args.task_id, args.title))

    delete_parser = commands.add_parser("delete", help="delete a task")
    delete_parser.add_argument("task_id", type=int)
    delete_parser.set_defaults(handler=lambda args: delete(args.task_id))

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    args.handler(args)
    return 0


def run() -> None:
    raise SystemExit(main())
