# Diagrams — task-manager-cli

## System diagram

```mermaid
graph TD
  User["👤 User"]
  CLI["CLI Parser<br/>(main.go)"]
  Dispatcher["Command Dispatcher"]
  TaskMgr["Task Manager<br/>(tasks.go)"]
  FileIO["File I/O<br/>(tasks.go)"]
  JsonFile["📄 ~/.task-manager.json"]

  User -->|"command args"| CLI
  CLI -->|"parsed command"| Dispatcher
  Dispatcher -->|"add/list/view/edit/delete/status"| TaskMgr
  TaskMgr -->|"read tasks"| FileIO
  FileIO -->|"load"| JsonFile
  TaskMgr -->|"write tasks"| FileIO
  FileIO -->|"persist"| JsonFile
  TaskMgr -->|"result or error"| CLI
  CLI -->|"formatted output"| User
```

---

## Overview

- Standalone CLI tool that reads tasks from a JSON file, applies mutations in-memory, and persists changes immediately
- User runs commands (`tm add`, `tm list`, `tm delete`, etc.); each invocation loads, modifies, saves, and exits
- All state lives in `~/.task-manager.json`; no network, no background processes

```mermaid
graph TD
  User["👤 User"]
  CLITool["🔧 CLI Tool<br/>(main.go + tasks.go)"]
  Storage["💾 Task Storage<br/>(~/.task-manager.json)"]

  User -->|"command"| CLITool
  CLITool -->|"load / persist"| Storage
  CLITool -->|"output"| User
```

- Reading it: User invokes a command → CLI loads tasks, applies logic, saves → output returned to user.
- Detail below: CLI Tool, Task Storage.

## CLI Tool

- Does: Parses command-line arguments; dispatches to task operations; formats and displays results; handles all user I/O and validation
- Takes in: Shell command with subcommand, arguments, and optional flags from the user
- Sends out: Formatted task data or error messages to stdout/stderr; exit code 0 on success, non-zero on error

**Internal flow:**
```mermaid
graph TD
  Input["Command input"]
  Parse["Parse args<br/>(subcommand, args, flags)"]
  Validate["Validate<br/>(required args, status values)"]
  Dispatch["Dispatch<br/>(add/list/view/edit/delete/status)"]
  Format["Format output<br/>(text or error)"]
  Output["stdout/stderr"]

  Input --> Parse
  Parse --> Validate
  Validate -->|valid| Dispatch
  Validate -->|invalid| Format
  Dispatch --> Format
  Format --> Output
```

## Task Storage

- Does: Stores tasks as JSON in `~/.task-manager.json`; handles read/write with error checking; manages file creation on first use
- Takes in: Tasks to persist (from CLI after mutations); requests to load tasks
- Sends out: Task data (on load); confirmation of successful save; error messages (corrupted JSON, permission denied, etc.)

**Internal structure:**
```mermaid
graph TD
  WriteReq["Write request<br/>(tasks array)"]
  ReadReq["Read request"]
  
  ReadReq --> FileCheck["Check if file exists"]
  FileCheck -->|exists| ParseJson["Parse JSON<br/>(validate v1 schema)"]
  FileCheck -->|missing| InitEmpty["Initialize empty<br/>(version: 1, tasks: [])"]
  ParseJson -->|valid| ReturnTasks["Return tasks array"]
  ParseJson -->|invalid| Error1["Error: corrupted JSON"]
  InitEmpty --> ReturnTasks
  
  WriteReq --> Encode["Encode tasks to JSON<br/>(with version: 1)"]
  Encode --> Write["Write to<br/>~/.task-manager.json"]
  Write -->|success| Confirm["Persist confirmed"]
  Write -->|permission error| Error2["Error: cannot write"]
  
  Error1 --> Halt1["Exit with error"]
  Error2 --> Halt2["Exit with error"]
```

