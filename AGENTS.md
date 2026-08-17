# AGENTS.md — <project> (project rules)

Read by every agent in this repo. Durable project knowledge only —
NOT the loop protocol (ralph_prompt.md), NOT the system conventions (CONVENTIONS.md).

## Output style
All generated prose uses short, precise bullet points. Plain language, no jargon,
no filler. Prefer a five-word bullet to a sentence.
- Applies to EXPLANATORY content in every document.
- Does NOT override required structured formats: keep Gherkin GIVEN/WHEN/THEN,
  tasks.md `- [ ] N.Y` checkboxes, ADR sections, and YAML front-matter exactly.

## Stack
<!-- languages, frameworks, key libraries -->

## Repo map
<!-- the main components/data and where they live -->

## Verification gate — quality checks
<!-- the exact commands that prove a change is correct in THIS project -->

## Sandbox — review mode execution
<!-- Read by /review-sandbox. Authoritative for THIS project. If empty, /review-sandbox
     stops and asks rather than improvising an environment.
     - Isolate:   how to make a throwaway copy + env at a pinned commit
                  e.g. git worktree add --detach sandbox/tree <sha>
                       python -m venv sandbox/env && sandbox/env/bin/pip install -r requirements.txt
                  R:   renv::restore(project = "sandbox/tree")
     - Run one:   the command that runs a single generated test
                  e.g. sandbox/env/bin/pytest sandbox/tests/<id>.py -q
                  R:   Rscript -e 'testthat::test_file("sandbox/tests/<id>.R")'
     - Stub:      how third-party boundaries are faked (monkeypatch, mockery, DI)
     - Never run: live DB, paid API, licensed solver, anything with a real credential.
                  These become `unproven`, never guessed. -->

## Hard rules
<!-- project-specific don'ts. Universal ones live in CONVENTIONS.md. -->

## Learnings
<!-- accumulates as the loop and you discover gotchas. Starts empty. -->