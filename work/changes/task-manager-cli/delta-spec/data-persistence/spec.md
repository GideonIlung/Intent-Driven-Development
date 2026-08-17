## ADDED Requirements

### Requirement: Persist tasks to JSON file

#### Scenario: Save tasks to file
- GIVEN tasks have been created or modified
- WHEN the user performs an operation that changes task state
- THEN the tasks are saved to ~/.task-manager.json in the specified JSON format

### Requirement: Load tasks from file

#### Scenario: Load existing tasks on startup
- GIVEN the file ~/.task-manager.json exists with valid task data
- WHEN the CLI tool starts
- THEN all tasks are loaded and available for operations

#### Scenario: Initialize empty task list
- GIVEN the file ~/.task-manager.json does not exist
- WHEN the CLI tool starts
- THEN an empty task list is created and ready to use

### Requirement: JSON file format

#### Scenario: Tasks stored in correct structure
- GIVEN tasks are being saved
- WHEN the file is written
- THEN the file contains a JSON object with a "tasks" array, each task having id, title, description, status, and createdAt fields

### Requirement: File I/O error handling

#### Scenario: Handle corrupted JSON file
- GIVEN the file ~/.task-manager.json contains invalid JSON
- WHEN the tool attempts to load tasks
- THEN an error is shown and the user is prompted to recover or reinitialize

#### Scenario: Handle permission errors
- GIVEN the file ~/.task-manager.json cannot be written due to permissions
- WHEN a task operation attempts to save
- THEN an error is shown indicating the permission issue
