## 1. Python command foundation
- [ ] 1.1 Create the Python project and the `todo` command entry point.
- [ ] 1.2 Parse `add`, `list`, `complete`, `edit`, and `delete` commands and their arguments.
- [ ] 1.3 Add automated command-level test support.

## 2. Local task storage
- [ ] 2.1 Define task records with an identifier, text, and completion state.
- [ ] 2.2 Create and read `~/.todo/tasks.json` using the Python standard library.
- [ ] 2.3 Create the per-user data directory and file on the first successful task addition.
- [ ] 2.4 Report malformed task data without overwriting the file.

## 3. Task operations
- [ ] 3.1 Add outstanding tasks and display their identifiers.
- [ ] 3.2 List outstanding tasks by default.
- [ ] 3.3 List outstanding and completed tasks with `todo list --all`.
- [ ] 3.4 Mark a task complete by identifier.
- [ ] 3.5 Edit a task's text by identifier.
- [ ] 3.6 Delete a task by identifier.
- [ ] 3.7 Reject unknown task identifiers without changing saved tasks.

## 4. Behaviour verification
- [ ] 4.1 Test task creation and persistence across separate command runs.
- [ ] 4.2 Test default and all-task listing output.
- [ ] 4.3 Test completing, editing, and deleting a task.
- [ ] 4.4 Test clear failures for unknown task identifiers.
