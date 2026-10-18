"""Persistent storage for local tasks."""

import json
from pathlib import Path
from typing import Dict, List, Union


Task = Dict[str, Union[int, str, bool]]


class StorageError(Exception):
    """Raised when saved task data cannot be used."""


class TaskNotFoundError(StorageError):
    """Raised when a task identifier does not exist."""


def data_file() -> Path:
    return Path.home() / ".todo" / "tasks.json"


def load() -> List[Task]:
    path = data_file()
    if not path.exists():
        return []

    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise StorageError(f"could not read saved tasks: {error}") from error

    if not isinstance(document, dict) or set(document) != {"tasks"}:
        raise StorageError("saved task data has an invalid format")

    saved_tasks = document["tasks"]
    if not isinstance(saved_tasks, list):
        raise StorageError("saved task data has an invalid format")

    identifiers = set()
    for task in saved_tasks:
        if not _valid_task(task) or task["id"] in identifiers:
            raise StorageError("saved task data has an invalid format")
        identifiers.add(task["id"])

    return saved_tasks


def save(saved_tasks: List[Task]) -> None:
    path = data_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"tasks": saved_tasks}, indent=2) + "\n",
        encoding="utf-8",
    )


def create(title: str) -> Task:
    saved_tasks = load()
    next_id = max((int(task["id"]) for task in saved_tasks), default=0) + 1
    task: Task = {"id": next_id, "text": title, "completed": False}
    saved_tasks.append(task)
    save(saved_tasks)
    return task


def read_outstanding() -> List[Task]:
    return [task for task in load() if not task["completed"]]


def read_all() -> List[Task]:
    return load()


def mark_complete(task_id: int) -> Task:
    saved_tasks = load()
    task = _find(saved_tasks, task_id)
    task["completed"] = True
    save(saved_tasks)
    return task


def update_text(task_id: int, title: str) -> Task:
    saved_tasks = load()
    task = _find(saved_tasks, task_id)
    task["text"] = title
    save(saved_tasks)
    return task


def remove(task_id: int) -> None:
    saved_tasks = load()
    task = _find(saved_tasks, task_id)
    saved_tasks.remove(task)
    save(saved_tasks)


def _find(saved_tasks: List[Task], task_id: int) -> Task:
    for task in saved_tasks:
        if task["id"] == task_id:
            return task
    raise TaskNotFoundError(f"task {task_id} does not exist")


def _valid_task(task: object) -> bool:
    if not isinstance(task, dict) or set(task) != {"id", "text", "completed"}:
        return False
    task_id = task["id"]
    return (
        isinstance(task_id, int)
        and not isinstance(task_id, bool)
        and task_id > 0
        and isinstance(task["text"], str)
        and isinstance(task["completed"], bool)
    )
