---
description: Build a disposable sandbox from the review's pinned commit, turn each claimed scenario into a runnable test, execute them, and record confirmed / refuted / unproven. The only command in the harness that executes code outside Ralph. Never touches the working tree.
argument-hint: <slug> [--refresh] [--only <capability>]
---

**Argument**: `$ARGUMENTS`

Execute the review's claims. Every scenario written by `/review-continue` is a hypothesis;
this is where it gets falsified. Gate → build sandbox → generate tests → run → record.

This is the ONE read-only mode that runs code. It stays safe by construction: the sandbox
is a **copy at the pinned commit**, effectful dependencies are **stubbed from recorded
probes**, and nothing is ever written back. If you cannot isolate it, you do not run it —
you mark it `unproven`.

**Input**: `/review-sandbox <slug> [--refresh] [--only <capability>]`. If no slug, list
`work/reviews/*/` and ask. `--refresh` rebuilds a sandbox that already exists.
`--only` runs one capability's scenarios.

**Steps**

1. **Resolve + require inputs.** Need `scope.md` (with `commit:`), `functions.md`, and at
   least one `scenarios/<capability>/spec.md`. Missing → stop; finish drafting with
   `/review-continue`.

2. **Coherence gate — trace-check.** Run the `/trace-check` procedure against this review.
   Holes → STOP and show them. A description whose scenarios and diagram disagree is not
   worth executing. Proceed only when clean, or when the user explicitly waives a named hole.

3. **Read the sandbox contract.** `AGENTS.md` → `## Sandbox` is authoritative for THIS
   project: how to make an isolated environment, how to install pinned deps, how to run one
   test, how to assert. If that section is absent or empty, STOP and ask the user to fill it
   — do not improvise an environment for someone else's project.

4. **Build the sandbox.** Under `work/reviews/<slug>/sandbox/`:
   - `tree/` — the code at the pinned commit, isolated. Default: `git worktree add
     --detach sandbox/tree <commit>`. Never a symlink to the working tree; never the
     working tree itself.
   - `env/` — a fresh environment with dependencies at the versions in `inventory.md`
     (venv / renv / lockfile — `AGENTS.md` decides).
   - `stubs/` — one stub per library marked `stub` in `inventory.md`, exposing ONLY the
     surface listed there. Libraries marked `real` are NOT stubbed — they are installed and
     called, because a real call cannot be wrong about the library and a stub always can.
     Stub only to prevent an effect (network, DB, filesystem, clock, randomness, credentials,
     licence check), never for convenience.
     Every stub's fixture is a **recorded characterisation probe**, not an authored guess:
     call the real function once with the actual inputs, freeze the result under
     `fixtures/probe-<lib>-<fn>.*`, replay it. Where behaviour has to be understood first,
     work `code-inventory`'s evidence ladder — pinned signature and docs (`?fn`,
     `help(fn)`, `inspect.signature`), then the installed source, then the probe. Docs are
     secondary; a memory is not evidence.
     Record per stub in `sandbox/stubs/README.md`: pinned version, how the value was
     obtained, the inputs used, and the scenarios it gates — a wrong stub silently
     invalidates every scenario that runs through it.
   - `tests/` — generated tests. They live OUTSIDE `tree/` and import into it, so no
     generated file is ever mistaken for source.
   - `fixtures/` — inputs the GIVEN steps need.
   - Add `sandbox/` to `.gitignore` except `results.md`, `stubs/README.md`, and `tests/`.
   If a sandbox exists and `--refresh` was not passed, reuse it and say so.

5. **Generate tests from scenarios** (load `sandbox-probe`). One test per scenario, named
   for it, mapped 1-1:
   - GIVEN → fixtures + stub configuration
   - WHEN → the single call, using the exact signature from `functions.md`
   - THEN → one assertion on the observable outcome
   A scenario that cannot be expressed as a runnable test is `unproven` with the reason —
   never reworded into a weaker test that passes.

6. **Run.** Execute the suite in the sandbox. Network off unless `AGENTS.md` says otherwise.
   Wall-clock limit per test. Capture stdout, stderr, exit status, and the stub call log
   into `sandbox/results/<test-id>/`.

7. **Classify every scenario — exactly one of three.**
   - **confirmed** — the test ran and the THEN held.
   - **refuted** — the test ran and the THEN did not hold. Record expected vs observed.
   - **unproven** — could not be run (sandbox constraint from `scope.md`, missing fixture,
     needs a live dependency, non-deterministic).
   A test that errors before reaching its assertion is `unproven`, NOT `refuted` — unless
   the error IS the observable outcome under test.
   Retag each scenario in `scenarios/` from `@claimed` to `@confirmed` / `@refuted` /
   `@unproven`.

8. **Write `sandbox/results.md`.** Per scenario: status, evidence path, expected vs observed
   for refutations, blocking reason for unproven. Then the totals, and the stub assumptions
   that were in force.

9. **Stop.** Report the three counts and the refutations. Then:
   "Run `/review-finish <slug>` to write the review."

**Two-way resolution**: a refutation names a DISAGREEMENT between the code and the claim,
not a bug. The code may be wrong, or the scenario may have described it wrongly. Report both
readings; never pick a side. Same discipline as trace-check.

**Guardrails**
- NEVER execute against the working tree, a real database, a production credential, or a
  paid endpoint. Copy at the pinned commit, stubs for effects, network off by default.
- NEVER write back into `tree/`, into repo source, into durable `specs/` or `adr/`.
- If isolation cannot be achieved for a scenario, it is `unproven`. Not "probably fine".
- `AGENTS.md` → `## Sandbox` is authoritative; if it is missing, stop and ask.
- Generated tests live outside `tree/` and are never promoted into the repo's real suite
  here — that is a `/change-new`.
- `real` is the default treatment; stub only to prevent an effect. Never fake a pure library.
- A stub fixture is RECORDED from a probe, never authored from memory or from docs alone.
  Label any fixture that came from docs as the weaker evidence it is.
- A test that cannot be written honestly is `unproven`; never weaken an assertion to
  make it pass.
- Do not fix anything you find. A fix is `/change-new`.
- Ground truth is the runner's exit status, not your reading of the code.