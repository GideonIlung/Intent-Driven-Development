# Todo CLI product requirements

## Story 1: Python command foundation

- **Priority:** 1
- **Tasks:**
  - Create the Python project and the `todo` command entry point.
  - Parse `add`, `list`, `complete`, `edit`, and `delete` commands and their arguments.
  - Add automated command-level test support.
- **Acceptance criteria:** No standalone user scenario. This is enabling work for all later stories.

## Story 2: Local task storage

- **Priority:** 2
- **Tasks:**
  - Define task records with an identifier, text, and completion state.
  - Create and read `~/.todo/tasks.json` using the Python standard library.
  - Create the per-user data directory and file on the first successful task addition.
  - Report malformed task data without overwriting the file.
- **Acceptance criteria:**
  - **Reopen saved tasks**
    - GIVEN the user added the task "Buy milk" in an earlier command run
    - WHEN the user runs `todo list` in a new command run
    - THEN the output shows "Buy milk"

## Story 3: Task operations

- **Priority:** 3
- **Tasks:**
  - Add outstanding tasks and display their identifiers.
  - List outstanding tasks by default.
  - List outstanding and completed tasks with `todo list --all`.
  - Mark a task complete by identifier.
  - Edit a task's text by identifier.
  - Delete a task by identifier.
  - Reject unknown task identifiers without changing saved tasks.
- **Acceptance criteria:**
  - **Add a task**
    - GIVEN the user has no saved tasks
    - WHEN the user runs `todo add "Buy milk"`
    - THEN a new outstanding task with the text "Buy milk" is saved
    - AND the command shows the task's identifier
  - **List outstanding tasks**
    - GIVEN an outstanding task "Buy milk" and a completed task "Wash car"
    - WHEN the user runs `todo list`
    - THEN the output shows "Buy milk"
    - AND the output does not show "Wash car"
  - **List all tasks**
    - GIVEN an outstanding task "Buy milk" and a completed task "Wash car"
    - WHEN the user runs `todo list --all`
    - THEN the output shows "Buy milk"
    - AND the output shows "Wash car" as completed
  - **Complete a task**
    - GIVEN task 1 is outstanding with the text "Buy milk"
    - WHEN the user runs `todo complete 1`
    - THEN task 1 is recorded as completed
    - AND task 1 is absent from the default task list
  - **Edit a task**
    - GIVEN task 1 has the text "Buy milk"
    - WHEN the user runs `todo edit 1 "Buy bread"`
    - THEN task 1 has the text "Buy bread"
  - **Delete a task**
    - GIVEN task 1 has the text "Buy milk"
    - WHEN the user runs `todo delete 1`
    - THEN task 1 is absent from all task lists
  - **Complete an unknown task**
    - GIVEN task 1 is the only saved task
    - WHEN the user runs `todo complete 2`
    - THEN the command reports that task 2 does not exist
    - AND task 1 remains unchanged
  - **Edit an unknown task**
    - GIVEN task 1 is the only saved task
    - WHEN the user runs `todo edit 2 "Buy bread"`
    - THEN the command reports that task 2 does not exist
    - AND task 1 remains unchanged
  - **Delete an unknown task**
    - GIVEN task 1 is the only saved task
    - WHEN the user runs `todo delete 2`
    - THEN the command reports that task 2 does not exist
    - AND task 1 remains unchanged

## Story 4: Behaviour verification

- **Priority:** 4
- **Tasks:**
  - Test task creation and persistence across separate command runs.
  - Test default and all-task listing output.
  - Test completing, editing, and deleting a task.
  - Test clear failures for unknown task identifiers.
- **Acceptance criteria:** No standalone user scenario. This story verifies the scenarios assigned to Stories 2 and 3.

## Mapping notes

- Stories 1 and 4 are enabling and verification work; they have no independent user-facing scenario.
- Story 2 owns persistence across command runs.
- Story 3 owns the user-facing task commands and their failure behaviour.
