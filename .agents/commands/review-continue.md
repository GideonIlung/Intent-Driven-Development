---
description: Resume a review — advance to the next artifact (inventory, diagrams, functions, scenarios), or revise an existing one (warn-and-stop). Grill-me runs in both branches. Read-only on the working tree.
argument-hint: [slug] [artifact]
---

**Argument**: `$ARGUMENTS`

Resume a review. Two branches, chosen automatically:
- ADVANCE (default): draft the next artifact in dependency order.
- REVISE (when you name an artifact that already exists): re-grill and rewrite it,
  then warn about what it invalidated.

The chain and its dependencies:
```
scope ─► inventory ─┬─► diagrams ──┐
                    └─► functions ─┴─► scenarios ─► [/trace-check] ─► /review-sandbox ─► /review-finish
```
inventory requires scope · diagrams requires inventory · functions requires inventory ·
scenarios requires diagrams AND functions.

**Input**: `/review-continue [slug] [artifact]`
- `slug` — which review. If omitted, infer from context, else list `work/reviews/`.
- `artifact` — optional. If named AND it already exists on disk → REVISE. Otherwise → ADVANCE.

**Steps**

1. **Resolve the review.** If no slug, list `work/reviews/*/` (most-recent first) and ask
   with AskUserQuestion.

2. **Read state.** Read `scope.md` — the pinned `commit` governs every read from here on.
   Determine which artifacts are drafted vs missing: `inventory.md`, `diagrams/system.md`,
   `functions.md`, `scenarios/` (non-empty?).

3. **Choose branch.** Artifact named AND exists → REVISE. Else → ADVANCE.

---

**ADVANCE**

a. Pick the target: the first artifact whose dependencies are all drafted but which isn't
   written yet, in order inventory → diagrams → functions → scenarios.

b. Load the artifact's template, read its dependency files for context, and load the
   matching skill:

   - **inventory** → `code-inventory`. Grow the closure from `scope.md`'s entry points,
     splitting every import by the boundary policy. Write `inventory.md`. Every unresolved
     import is listed as unresolved — never guessed onto a side.

   - **diagrams** → `c4-diagrams`. Write `diagrams/system.md` following
     `templates/diagram.md` and its FIXED headings. For a review the graph is
     **function-level**:
     - `## System diagram` — one flat Mermaid graph. Nodes are the functions from the
       inventory's expanded set, plus ONE node per boundary library, plus external
       inputs/outputs. Edges are labelled with **what flows** (`raw rows`, `solved
       timetable`), because that is what makes the function reference and the scenarios
       checkable against it.
     - `## Overview` — the same graph grouped into ≤ 7-9 **processes**.
     - `## <process>` sections — one per Overview box, with Does / Takes in / Sends out.
     Then, one `diagrams/lib-<name>.md` per boundary library, same template, scoped to
     the surface actually used — NOT the whole library. A library documents its own
     boundary; it is never exploded into the System diagram.

   - **functions** → derive from `inventory.md` + the code at the pinned commit. One entry
     per function in the expanded set: signature, does, takes in, gives back, raises, side
     effects, calls, called by. Node ids MUST match `diagrams/system.md`. Read the body —
     never infer a signature from a name; the sandbox is built against this.

   - **scenarios** → `grill-me` + `gherkin-authoring`. Write one
     `scenarios/<capability>/spec.md` per process group, using the same headers as a
     delta-spec (`### Requirement:`, `#### Scenario:`, GIVEN/WHEN/THEN with observable
     outcomes) so `/trace-check` reads them unchanged.
     **These are CLAIMS, not contracts.** In a change, a scenario says what will be built.
     In a review it says what the code appears to do — a hypothesis the sandbox will try to
     falsify. Tag each `@claimed` on writing. Cover the ordinary path, each branch, each
     documented error, and each boundary interaction. Then fill `functions.md`'s Coverage
     section: any function no scenario exercises is a finding.

c. Grill against the template's slots (fill blanks). Apply skill rules as constraints;
   never copy template hints into the output.

d. Write that ONE artifact. Stop. Report what was written and what the next artifact is.
   After `scenarios`, say: "Run `/trace-check <slug>`, then `/review-sandbox <slug>`."

---

**REVISE**

a. Re-open the named artifact. Load `grill-me`. Grill on the GAP — the delta between what's
   written now and what's actually right — not empty-slot questions. Rewrite it.

b. **Warn and stop.** Compute the downstream artifacts (everything that transitively
   depends on the one revised):
   - scope → inventory, diagrams, functions, scenarios, sandbox, review
   - inventory → diagrams, functions, scenarios, sandbox, review
   - diagrams → scenarios, review
   - functions → scenarios, sandbox, review
   - scenarios → sandbox, review
   For each downstream artifact that EXISTS on disk, print it as STALE with a one-line
   reason and its repair command (`/review-continue <slug> <artifact>`, or
   `/review-sandbox <slug> --refresh`).
   Then state plainly: durable `specs/` is untouched, and any existing
   `sandbox/results.md` now describes a superseded description.
   Do NOT cascade and do NOT delete anything.

c. **Re-pin only on request.** If revising because the code moved, the user must say so
   explicitly; then update `commit:` in `scope.md` and mark EVERY artifact stale. Silent
   re-pinning invalidates the whole review without anyone noticing.

**Guardrails**
- One artifact per invocation — ADVANCE writes one; REVISE rewrites one and warns.
- grill-me runs in BOTH branches: empty slots on advance, the gap on revise.
- Everything is read at the pinned commit. Never mix commits within one review.
- READ-ONLY. Never edit code, durable `specs/`, or `adr/`. No execution here — that is
  `/review-sandbox`.
- Scenarios are claims (`@claimed`), never contracts. Nothing here proves behaviour;
  only the sandbox does.
- Boundary libraries are never exploded into `## System diagram` — one node, own document.
- REVISE over-warns by design.
- Template hints are constraints for you, not content for the file.
