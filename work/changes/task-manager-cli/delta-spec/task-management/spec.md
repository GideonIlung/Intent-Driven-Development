## ADDED Requirements

### Requirement: Add a new task

#### Scenario: Create a task with title only
- GIVEN the task list is empty
- WHEN the user runs `tm add "write report"`
- THEN a new task is created with a unique ID, title "write report", status "todo", and displayed to the user

#### Scenario: Create a task with title and description
- GIVEN the task list is empty
- WHEN the user runs `tm add "write report" --description "quarterly report"`
- THEN a new task is created with title, description, and status "todo"

### Requirement: List all tasks

#### Scenario: List tasks in default format
- GIVEN tasks exist with different statuses
- WHEN the user runs `tm list`
- THEN all tasks are displayed with ID, title, and status in a readable format

#### Scenario: Filter tasks by status
- GIVEN multiple tasks with different statuses exist
- WHEN the user runs `tm list --status inprogress`
- THEN only tasks with status "in progress" are displayed

### Requirement: View task details

#### Scenario: Display full task information
- GIVEN a task exists with ID "1"
- WHEN the user runs `tm view 1`
- THEN the task's ID, title, description, and status are displayed

#### Scenario: Handle missing task
- GIVEN no task with ID "99" exists
- WHEN the user runs `tm view 99`
- THEN an error message is shown

### Requirement: Update task status

#### Scenario: Change task status
- GIVEN a task with ID "1" has status "todo"
- WHEN the user runs `tm status 1 inprogress`
- THEN the task's status changes to "in progress"

#### Scenario: Set task to complete
- GIVEN a task with ID "1" has status "in progress"
- WHEN the user runs `tm status 1 complete`
- THEN the task's status changes to "complete"

### Requirement: Edit task content

#### Scenario: Update task title
- GIVEN a task with ID "1" exists
- WHEN the user runs `tm edit 1 --title "new title"`
- THEN the task's title is updated

#### Scenario: Update task description
- GIVEN a task with ID "1" exists
- WHEN the user runs `tm edit 1 --description "new description"`
- THEN the task's description is updated

### Requirement: Delete a task

#### Scenario: Delete with confirmation
- GIVEN a task with ID "1" exists
- WHEN the user runs `tm delete 1`
- AND confirms the deletion when prompted
- THEN the task is removed from the list

#### Scenario: Cancel deletion
- GIVEN a task with ID "1" exists
- WHEN the user runs `tm delete 1`
- AND declines the confirmation prompt
- THEN the task remains unchanged
