## Context

- A new standalone Python CLI manages a user's plain-text tasks.
- Tasks must remain available across separate command runs.
- The tool has no existing services or APIs to integrate with.

## Goals / Non-Goals

### Goals

- Provide `add`, `list`, `complete`, `edit`, and `delete` commands.
- Keep outstanding tasks as the default list output.
- Show completed tasks with `todo list --all`.
- Persist each user's tasks locally.

### Non-Goals

- Due dates, priorities, projects, reminders, synchronisation, or shared task lists.
- A graphical interface or network service.

## Decisions

- Implement the command in Python using the standard library.
  - Avoids third-party runtime dependencies for a small local utility.
  - Considered external CLI frameworks; they add setup and dependency overhead.
- Store tasks as JSON in `~/.todo/tasks.json`.
  - Supports task identifiers, text, and completion state in one readable per-user file.
  - Considered a plain line-based file; it cannot safely represent completion state and stable identifiers.
- Separate command handling from task operations and file persistence.
  - Keeps command parsing, task rules, and storage changes independently testable.

## Risks / Trade-offs

- [Corrupt local JSON prevents task access] -> Report a clear error and do not overwrite the file.
- [Concurrent commands can overwrite changes] -> Keep operations short; concurrent access is not supported in this first version.
- [Users expect tasks to sync] -> Document that tasks are local to one user and machine.

## Migration Plan

- No migration is required because no prior task data exists.
- Create `~/.todo/` and the task file on the first successful task addition.

## Open Questions

- None.
