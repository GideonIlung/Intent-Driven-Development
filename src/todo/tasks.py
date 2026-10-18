"""Task operations."""

from typing import NoReturn

from todo import store


def _not_implemented() -> NoReturn:
    raise NotImplementedError("task operations are not implemented")


def add(title: str) -> store.Task:
    return store.create(title)


def list_outstanding():
    return store.read_outstanding()


def list_all() -> NoReturn:
    _not_implemented()


def complete(task_id: int) -> NoReturn:
    _not_implemented()


def edit(task_id: int, title: str) -> NoReturn:
    _not_implemented()


def delete(task_id: int) -> NoReturn:
    _not_implemented()
