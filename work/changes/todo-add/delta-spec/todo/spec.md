## ADDED Requirements

### Requirement: Create tasks
The system SHALL let a user create a plain-text task with the `todo add` command.

#### Scenario: Add a task
- GIVEN the user has no saved tasks
- WHEN the user runs `todo add "Buy milk"`
- THEN a new outstanding task with the text "Buy milk" is saved
- AND the command shows the task's identifier

### Requirement: List tasks
The system SHALL list outstanding tasks by default and all tasks when requested.

#### Scenario: List outstanding tasks
- GIVEN an outstanding task "Buy milk" and a completed task "Wash car"
- WHEN the user runs `todo list`
- THEN the output shows "Buy milk"
- AND the output does not show "Wash car"

#### Scenario: List all tasks
- GIVEN an outstanding task "Buy milk" and a completed task "Wash car"
- WHEN the user runs `todo list --all`
- THEN the output shows "Buy milk"
- AND the output shows "Wash car" as completed

### Requirement: Complete tasks
The system SHALL let a user mark a task complete with its identifier.

#### Scenario: Complete a task
- GIVEN task 1 is outstanding with the text "Buy milk"
- WHEN the user runs `todo complete 1`
- THEN task 1 is recorded as completed
- AND task 1 is absent from the default task list

### Requirement: Edit tasks
The system SHALL let a user change a task's plain-text description with its identifier.

#### Scenario: Edit a task
- GIVEN task 1 has the text "Buy milk"
- WHEN the user runs `todo edit 1 "Buy bread"`
- THEN task 1 has the text "Buy bread"

### Requirement: Delete tasks
The system SHALL let a user permanently delete a task with its identifier.

#### Scenario: Delete a task
- GIVEN task 1 has the text "Buy milk"
- WHEN the user runs `todo delete 1`
- THEN task 1 is absent from all task lists

### Requirement: Preserve tasks
The system SHALL preserve task changes in a per-user local data file between command runs.

#### Scenario: Reopen saved tasks
- GIVEN the user added the task "Buy milk" in an earlier command run
- WHEN the user runs `todo list` in a new command run
- THEN the output shows "Buy milk"

### Requirement: Reject unknown task identifiers
The system SHALL reject an action targeting a task identifier that does not exist without changing saved tasks.

#### Scenario: Complete an unknown task
- GIVEN task 1 is the only saved task
- WHEN the user runs `todo complete 2`
- THEN the command reports that task 2 does not exist
- AND task 1 remains unchanged

#### Scenario: Edit an unknown task
- GIVEN task 1 is the only saved task
- WHEN the user runs `todo edit 2 "Buy bread"`
- THEN the command reports that task 2 does not exist
- AND task 1 remains unchanged

#### Scenario: Delete an unknown task
- GIVEN task 1 is the only saved task
- WHEN the user runs `todo delete 2`
- THEN the command reports that task 2 does not exist
- AND task 1 remains unchanged
