"""Task operations implemented by later stories."""

from typing import NoReturn


def _not_implemented() -> NoReturn:
    raise NotImplementedError("task operations are not implemented")


def add(title: str) -> NoReturn:
    _not_implemented()


def list_outstanding() -> NoReturn:
    _not_implemented()


def list_all() -> NoReturn:
    _not_implemented()


def complete(task_id: int) -> NoReturn:
    _not_implemented()


def edit(task_id: int, title: str) -> NoReturn:
    _not_implemented()


def delete(task_id: int) -> NoReturn:
    _not_implemented()
