---
type: implementation
id: todo-add
tag: impl/todo-add
---

## Why

Users need a quick way to see and manage tasks that still need completing.

## What Changes

- Add a standalone `todo` command-line tool.
- Add commands to create, list, complete, edit, and delete plain-text tasks.
- Save each user's tasks in a local per-user data file.

## Capabilities

### New Capabilities

- `todo`: Manage locally persisted plain-text tasks from the `todo` command.

### Modified Capabilities

- None.

## Impact

- New command-line interface and task-management code.
- New per-user task data file.
- No existing APIs, services, or capabilities change.
