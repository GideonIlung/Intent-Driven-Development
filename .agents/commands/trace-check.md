---
description: Check that a change's C4 diagram and its Gherkin scenarios agree. Walks each Given/When/Then across the diagram's components and reports holes. Read-only, change-scoped, prints to chat — writes nothing.
argument-hint: [slug]
---

**Argument**: `$ARGUMENTS`

Coherence lint for one change: cross-reference its C4 diagram (structure) against its
Gherkin scenarios (behaviour) and report where they disagree. Executes nothing —
"check" means the two documents are consistent with each other, caught before code.
The result is printed to chat only; NO file is written (a persisted lint result goes
stale the instant either document is edited).

**Input**: `/trace-check [slug]` — the change under `work/changes/<slug>/`. If omitted,
list `work/changes/*/` and ask.

**Steps**

1. **Resolve + confirm inputs.** Locate the change. Confirm it has both a C4 diagram
   (in `diagrams/`, or fenced Mermaid in `design.md`) AND at least one
   `delta-spec/<capability>/spec.md`. If either is missing, stop and say which — this is
   change-only and needs the pair; do not guess.

2. **Build the inventory from the C4.** Extract components (boxes / Mermaid nodes),
   connections (arrows / edges, with direction), and external inputs/outputs. This is the
   model the scenarios are checked against.

3. **Trace every scenario.** For each `#### Scenario:` block, take its steps in order and
   land each on the inventory:
   - **GIVEN** (state): a component or input that establishes/carries it?
   - **WHEN** (one event): a component that receives it, with a path (arrow) to it?
   - **THEN** (observable outcome): a component that produces/checks it, reachable along
     the flow?
   A scenario passes only if every step lands and the steps form a connected path.

4. **Classify each miss.**
   - **Missing component** — a responsibility no box covers.
   - **Unrouted input** — a GIVEN box exists but no arrow carries it to the WHEN.
   - **Unowned outcome** — a THEN no component produces/checks.
   - **Orphan component** (reverse pass) — a box no scenario exercises.

5. **Print the report and stop.** Read-only. Edit nothing.

**Two-way resolution**: a hole never says which document is wrong, only that they
disagree. Report the disagreement and BOTH fixes (patch the diagram, or drop the
scenario's assumption); let the user choose.

**Output** (to chat, no file):
```
trace-check · <slug>
Inventory: <n> components, <n> connections   Scenarios: <n> checked

✓ <capability> / <scenario>
✗ <capability> / <scenario>
    WHEN "<step>"  → unrouted input: availability reaches no component
       fix: add availability input+arrow to the C4, OR drop the assumption

Orphans: <component>
Summary: <n> passed, <n> with holes.
```

**What it does not do**: structural completeness only — not correctness, not runtime, not
solver feasibility, not whether the C4 matches the real R code. It is a lint, not a proof.
Execution is Cucumber/Ralph after code; soundness is TLA+/Alloy. This is neither.

**Guardrails**
- Read-only, prints to chat, writes no file.
- Change-scoped; requires the C4 + delta-spec pair. Missing either → stop.
- Over-report ambiguous cases rather than silently pass (same bias as warn-and-stop).
- Never pick which document is wrong; report both fixes.
