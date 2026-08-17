---
name: sandbox-probe
description: Use when turning Gherkin scenarios into runnable tests against existing code, building an isolated sandbox to execute code under review, stubbing third-party dependencies at a boundary, or classifying a test outcome as confirmed, refuted, or unproven. Use for review mode's sandbox step.
---

# Sandbox Probe

## Overview
Turn each claimed scenario into ONE runnable test against a copy of the code, run it, and
classify the outcome. The tests exist to FALSIFY the description, not to pass. A green suite
that was made green by weakening assertions is worse than no suite — it launders a guess
into evidence.

## Isolation — non-negotiable
- Code under test is a **copy at the pinned commit** (`git worktree add --detach`). Never
  the working tree, never a symlink to it.
- Dependencies installed fresh at the versions in `inventory.md`.
- Boundary libraries **stubbed**; stdlib usually real.
- Network **off** by default. No real database, no credential, no paid endpoint.
- Generated tests live OUTSIDE the copied tree and import into it.
- Nothing is written back — not to the tree, not to repo source, not to durable docs.
If a scenario cannot be run under these conditions, it is `unproven`. Never relax isolation
to get a result.

## Scenario → test, 1-1
| Gherkin step | Becomes |
| --- | --- |
| GIVEN | fixtures + stub configuration (the starting state) |
| WHEN | exactly one call, using the signature from `functions.md` |
| THEN | one assertion on the observable outcome |
| AND after THEN | one more assertion |

Name the test for the scenario so `results.md` maps back without ambiguity. One scenario,
one test. If a scenario needs two calls to express, the scenario is wrong — say so rather
than splitting it silently.

## Real by default; stub only for effects
A boundary library is not automatically stubbed. Run it **real** unless it would cause an
effect you must not cause — network, DB, filesystem outside a temp dir, clock, randomness,
credentials, a licence check. `code-inventory`'s treatment column is authoritative.

A real call cannot be wrong about the library. A stub always can. So the bar for stubbing is
an effect, never convenience.

## Stubs are RECORDED, not invented
When a stub is genuinely required, its fixture comes from a **characterisation probe**, not
from what you believe the library returns.

1. **Probe.** Call the real function once, in the sandbox, with the actual inputs this code
   passes it. Capture the return value, its type/shape, and any error.
   - unavoidably effectful (a live DB)? probe against a local equivalent — a temp SQLite
     file, a throwaway table — and record that substitution as an assumption.
   - cannot be probed at all? every scenario through it is `unproven`. Not a guess.
2. **Freeze.** Save the recorded value under `sandbox/fixtures/probe-<lib>-<fn>.<ext>`.
3. **Replay.** The stub returns the frozen value and records its calls, so a scenario can
   assert on the interaction as well as the return.
4. **Attribute.** In `sandbox/stubs/README.md`, per stub: the pinned version, how the value
   was obtained (probed / probed against a substitute / read from docs), the inputs used, and
   the scenarios it gates.

Before writing any stub, settle the behaviour via `code-inventory`'s evidence ladder — pinned
signature and docs (`?fn`, `help(fn)`, `inspect.signature`), then the installed source, then
the probe. Docs are secondary evidence: a probe beats a doc, a doc beats a memory, and a
memory is not evidence. A stub whose fixture came from docs alone is labelled as such,
because it is weaker than one built from a recorded call.

A wrong stub turns a false claim into `confirmed` — the single most dangerous failure mode of
the whole mode, and the reason the fixture must be recorded rather than authored.

## Classification — exactly one of three
- **confirmed** — the test ran and the THEN held.
- **refuted** — the test ran and the THEN did not hold. Record expected vs observed.
- **unproven** — could not be run honestly: a sandbox constraint from `scope.md`, a missing
  fixture, a live dependency, non-determinism, or a test that errored before reaching its
  assertion.

An error before the assertion is `unproven`, not `refuted` — unless the error IS the
observable outcome under test, in which case it was the THEN all along.

Non-determinism: run it three times. Same answer → classify. Different answers → `unproven`
with the variance recorded, which is itself a finding.

## Two-way resolution
A refutation names a disagreement between the code and the claim. The code may be wrong, or
the scenario may have described it wrongly. Report both readings. Never pick a side, and
never edit the scenario to match the code — that erases the finding.

## Evidence
Per test, capture stdout, stderr, exit status and the stub call log under
`sandbox/results/<test-id>/`. A status with no evidence path is not a result.

## Common mistakes
| Mistake | Fix |
| --- | --- |
| Weakening an assertion until it passes | Keep the assertion; mark `unproven` if it can't run. |
| Running against the working tree "just this once" | Copy at the pinned commit. Always. |
| Guessing what a stubbed library returns | Probe the real call and freeze the result. |
| Stubbing a pure library for convenience | Run it real. Stub only to avoid an effect. |
| Settling library behaviour from memory | `?fn` / `help(fn)` in the PINNED env, then probe. |
| Reading docs from your local version | Read them inside the sandbox env; versions differ. |
| Calling a test that errored a refutation | Errors before the assertion are `unproven`. |
| Rewriting a refuted scenario to match the code | The refutation is the finding. Leave it. |
| Fixing the bug you just found | Not here. That is `/change-new`. |
| Promoting generated tests into the repo's suite | Also `/change-new`. |
| A status with no evidence path | Capture the run, or it didn't happen. |