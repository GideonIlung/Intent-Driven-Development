# Intent-Driven Template

- Spec-first workflow for AI-agent development.
- You author what you're building as reviewable documents; a build loop (Ralph) implements it.
- A durable, versioned record of *what the system does* and *why* stays current as you go.
- Running example throughout: a terminal task manager (`toy-todo`).

## What you get
- Two modes: **implementation** (build something) and **investigation** (analyse, read-only).
- A living map of the system: `specs/` (behaviour) + `adr/` (decisions).
- A loop that turns approved specs into code, gated by real tests.
- A git tag on every finished piece of work — roll back by name.

## Layout
- `specs/` — durable. What the system does. Gherkin scenarios + C4 diagrams. Append-only.
- `adr/` — durable. Decision log. Immutable; superseded, never edited.
- `work/` — transient. Where documents are authored. Safe to prune.
- `templates/` — artifact skeletons.
- `.opencode/` — the commands and skills.
- `AGENTS.md` — per-project rules + the verification gate. **Fill this first.**
- `ralph.sh`, `ralph_prompt.md` — the build loop.
- `finalise.sh` — commit + tag a finished document.
- Keep the `.gitkeep` files — they hold the empty dirs in git.

## Setup
- Copy the template into a new repo.
- `git init && git add -A && git commit -m scaffold`
- Fill `AGENTS.md`: Stack, Repo map, and the **Verification gate** (the checks that prove a change works).
  - toy-todo: stack = Python + pytest; gate = `pytest -q` passes.
- Install tools. toy-todo: `pip install pytest`.

## Modes
- **Implementation** → `work/changes/<slug>/`. Full artifact chain. Ends in code + updated `specs/`.
- **Investigation** → `work/investigations/<slug>/`. One read-only report. Never edits code.

## Commands

### `/change-new <slug>`
- Starts an implementation change.
- Grills you, confirms the structure, scaffolds the proposal, stops.
- toy-todo: `/change-new add-and-list-tasks` → defines capability `task-management`.

### `/change-continue <slug> [artifact]`
- Draws the next artifact: proposal → delta-spec → design → adr → tasks.
- One artifact per run; run it repeatedly.
- Name an artifact to **revise** it: `/change-continue add-and-list-tasks delta-spec`.
- Revising an upstream doc flags stale downstream docs — no auto-cascade.

### `/trace-check <slug>`
- Checks the C4 diagram and the Gherkin scenarios agree.
- Read-only; prints to chat; writes no file.
- toy-todo: flags a "list tasks" scenario if the diagram has no list component.

### `/change-ship <slug>`
- Prepares the change for Ralph.
- trace-check gate → writes `prd.md` for your final review → converts to `prd.json`.
- toy-todo: confirm "add" and "list" map to the right acceptance criteria.

### `./ralph.sh`
- The build loop. Fresh agent each iteration.
- Builds one story, runs the gate, commits only when green.
- Stops when every story passes. Set `RALPH_MODEL` to a model you have.
- toy-todo: writes `src/todo/` + tests until `pytest` is green.

### `/change-finish <slug>`
- Run after Ralph passes.
- Verifies every story passed → reconciles → archives into `specs/` → tags `impl/<slug>`.
- toy-todo: `specs/task-management/` now exists.

### `/investigate-new <slug>`
- Starts a read-only investigation.
- Grills the symptom, traces to a proven root cause, writes a report.
- Never edits code. A fix becomes a new `/change-new`.
- toy-todo: `/investigate-new list-shows-duplicates`.

### `/investigate-continue <slug>`
- Refines an existing report; re-grills the gaps.
- Read-only; one document; no cascade.

### `/baseline [capability]`
- One-time, for existing code. Seeds `specs/` + `adr/` from what the code already does.
- Reads the real code; one capability per run.
- Skip on a greenfield project like toy-todo.

### `bash finalise.sh <lead-doc>`
- Commits + tags a finished document from its front-matter.
- Change → `impl/<slug>` (undo with `git revert`). Investigation → `inv/<slug>` (a bookmark).
- Called automatically by `/change-finish`; run by hand to close an investigation.

## Flow — implementation (toy-todo)
```
/change-new add-and-list-tasks
/change-continue add-and-list-tasks     # ×4: delta-spec, design, adr, tasks
/trace-check add-and-list-tasks         # optional
/change-ship add-and-list-tasks         # review prd.md, then prd.json
./ralph.sh                              # builds until pytest is green
/change-finish add-and-list-tasks       # archive into specs/, tag impl/
```

## Flow — investigation (toy-todo)
```
/investigate-new list-shows-duplicates
/investigate-continue list-shows-duplicates       # refine
bash finalise.sh work/investigations/list-shows-duplicates/report.md
```

## Rollback
- `git tag -l 'impl/*'` — completed changes.
- `git tag -l 'inv/*'` — investigations.
- `git revert <commit>` — undo a change.
- `git checkout <tag>` — inspect a past state.

## Rules
- One artifact per `/change-*` run; one story per Ralph iteration.
- Ralph never touches `specs/` or `adr/` — `/change-finish` owns that.
- Investigations never edit code.
- Fill `AGENTS.md`'s verification gate before running Ralph, or it has nothing to check.
