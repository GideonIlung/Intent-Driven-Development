"""Task operations."""

from todo import store


def add(title: str) -> store.Task:
    return store.create(title)


def list_outstanding():
    return store.read_outstanding()


def list_all():
    return store.read_all()


def complete(task_id: int) -> store.Task:
    return store.mark_complete(task_id)


def edit(task_id: int, title: str) -> store.Task:
    return store.update_text(task_id, title)


def delete(task_id: int) -> None:
    store.remove(task_id)
