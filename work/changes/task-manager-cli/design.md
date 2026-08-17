## Context

A standalone CLI tool for personal task management. User invokes commands like `tm add "task"`, `tm list`, `tm delete 1` to manage a persistent list of tasks stored in `~/.task-manager.json`. Single-user, single-machine tool; no network or concurrency concerns.

## Goals / Non-Goals

**Goals:**
- Enable fast task creation, listing, and status updates from the terminal
- Persist all changes immediately to disk (write after every mutation)
- Provide clear error messages and validation feedback
- Keep implementation simple and dependency-free (manual CLI parsing)

**Non-Goals:**
- Multi-user or networked task management
- Complex filtering, sorting, or search beyond status-based filtering
- Task collaboration or sharing
- Import/export of non-JSON formats
- Graphical UI or web interface

## Decisions

**Language: Go** — Compiles to single binary, excellent for CLI tools, built-in time/JSON support.

**Structure: Flat with two files** — `main.go` for CLI parsing and command dispatch; `tasks.go` for task model and file I/O. Keeps code simple while maintaining separation of concerns.

**CLI Parsing: Manual os.Args parsing** — No external CLI library. Trade off some robustness for zero dependencies and full control over behavior.

**Task IDs: Sequential integers** — Track max ID from the tasks array; calculate next ID on each write. Simple, human-friendly for `tm view 1`, handles gaps from deletions gracefully.

**JSON structure:** 
- Root object with `"version"` (currently 1) and `"tasks"` array
- Calculate next ID as `max(tasks[].id) + 1` on each write
- No separate nextId counter; self-healing if file is edited manually

```json
{
  "version": 1,
  "tasks": [
    {
      "id": 1,
      "title": "Write report",
      "description": "Quarterly review",
      "status": "todo",
      "createdAt": "2026-08-06T14:30:00Z"
    }
  ]
}
```

**Write timing: After every mutation** — Each `add`, `status`, `edit`, `delete` command immediately writes to disk. Each invocation is stateless: load → mutate → save → exit.

**Error handling: Fail hard** — Corrupted JSON or permission errors print a clear error and exit. No automatic recovery or prompts. User must manually fix the file or delete it to reset.

**Output format: Simple text** — One task per line, minimal alignment. For `list`, show `id. title (status)`. For `view`, show all fields as `key: value` pairs.

**Status values: Five fixed options** — `todo`, `inprogress`, `complete`, `blocked`, `archived`. Validate strictly; reject unknown statuses with a clear error message listing valid options.

**Delete confirmation: Interactive prompt** — `tm delete <id>` prompts the user on stdout: `Delete task 1 "..."? (y/n):`. Reading from stdin; no `--force` flag (can add later if scripting becomes critical).

**Timestamps: ISO8601 format** — Store `createdAt` as `"2026-08-06T14:30:00Z"`. Human-readable in the JSON file; Go's `time.Time` parses and formats natively.

**Data file location: Hardcoded** — Always `~/.task-manager.json`. Standard Unix pattern (like `.bashrc`); no env var configuration. Simplicity over flexibility at this stage.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Manual CLI parsing is error-prone** | Unit tests validate all command parsing and edge cases. Keep the parser simple (no complex nesting). |
| **Write-on-every-mutation is slower than batching** | Acceptable for single-user tool; each invocation is ~ms-scale. |
| **No concurrency control; race conditions if two invocations run simultaneously** | Documented as single-user, single-machine tool. If concurrent access becomes real, add file locking. |
| **Corrupted JSON causes hard failure** | User can recover by deleting the file (`rm ~/.task-manager.json`). Could add backup strategy later. |
| **Hardcoded file path limits flexibility** | Can add env var support later. Current simplicity outweighs hypothetical future flexibility. |

## Migration Plan

First version (this change) implements all core functionality: add, list, view, edit (status + title/description), delete. No migration needed.

Future extensions (e.g., priority, due dates, tags) will need:
1. Update the JSON schema (add new fields to tasks)
2. Increment `version` field in the JSON root
3. Read tasks and populate missing fields with defaults

No migration code in this version.

## Open Questions

- **Testing environment:** Should we test against a temporary `~/.task-manager.json` or mock the file I/O entirely? (Likely: use a temp file in `t.TempDir()` for integration tests, mock for unit tests of logic.)
- **Help text:** How much detail in `tm --help`? (Likely: brief usage, list subcommands with one-line descriptions, suggest `tm help <command>` for subcommand help.)
- **Initial empty state:** When the tool runs for the first time and `~/.task-manager.json` doesn't exist, should we create it immediately or only on the first `add`? (Likely: create it on first `add` for minimal footprint.)

