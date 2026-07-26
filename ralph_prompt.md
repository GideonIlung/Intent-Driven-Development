# Ralph iteration prompt — implementation build

You are a FRESH instance with no memory of previous iterations. All state lives on disk;
reconstruct it before doing anything. Your job this iteration: build ONE story from
`prd.json` into working code, proven against its acceptance criteria and the project's
verification gate. You BUILD — you do not author specs, archive, or investigate.

## 1. Reconstruct context
- `prd.json` — the stories. Each has `id`, `title`, `priority`, `passes`, and
  `acceptanceCriteria` (Gherkin scenarios — the definition of done).
- `progress.txt` — learnings from prior iterations (may be empty).
- `AGENTS.md` — project rules, the verification gate, quality-check commands, learnings.
- `git log --oneline -10` — what is already done.
- For context on the current story you MAY read the change folder it came from
  (`work/changes/<slug>/design.md`, `delta-spec/`), but the `acceptanceCriteria` in
  `prd.json` are authoritative for "done".

## 2. Do exactly ONE story
- Pick the highest-priority story (lowest `priority` number) where `passes: false`.
- Work on ONLY that story. Never start a second.
- Implement it so EVERY `acceptanceCriteria` scenario is satisfied. Keep changes minimal
  and scoped (see AGENTS.md hard rules).

## 3. Verify — two parts, both must hold
- **The project gate**: run the quality checks defined in `AGENTS.md` and confirm they
  pass. What those checks are is project-specific; `AGENTS.md` is authoritative.
- **The story's criteria**: every `acceptanceCriteria` scenario is observably true
  (Given/When/Then).

### If BOTH pass
- Commit. Message: `<story-id>: <title>`.
- Set that story's `passes` to `true` in `prd.json`.
- Append a one-line note to `progress.txt` (what you did + any gotcha).
- If you found a reusable pattern, add it under **Learnings** in `AGENTS.md`.
- Then stop. The loop starts the next iteration.

### If EITHER fails
- Do NOT commit. Do NOT mark the story passed.
- Append what went wrong to `progress.txt` so the next iteration avoids it.
- Then stop.

## Rules
- One story per iteration.
- Never modify a story already marked `passes: true`.
- Keep changes minimal and scoped to the current story.
- Commit ONLY when BOTH checks pass — a broken commit poisons later iterations.
- Never touch durable `specs/` or `adr/` — that is `/change-finish`'s job, not the loop's.
- Never guess; prove against the real repo (see AGENTS.md).