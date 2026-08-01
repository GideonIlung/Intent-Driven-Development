---
description: One-time ground-zero for an EXISTING codebase — read the real code and seed durable specs/<capability> and adr/ to reflect current reality. Incremental, one capability per run. The deliberate exception that writes the durable layer directly (not a change).
argument-hint: [capability]
---

**Argument**: `$ARGUMENTS`

Establish the baseline for a brownfield repo: document what the code ALREADY does into
the durable layer. This is the ONE deliberate exception to "durable only changes via
archive" — there is no change to propose, you are recording existing reality. After
baseline, all further edits go through the change flow (`/change-new` → archive).

**CRITICAL — describe reality, proven by reading the code.** Every requirement and
scenario must reflect what the functions ACTUALLY do, verified by reading them — never
assumption, memory, or aspiration. Everything is written as `ADDED` (first appearance),
so this becomes the baseline every future `MODIFIED` diffs against. An inaccurate
baseline silently corrupts every change after it. When the code and your expectation
disagree, the code wins; when behaviour is genuinely unclear, say so — do not invent it.

**Input**: `/baseline [capability]` — the capability to document (kebab-case). If omitted,
help the user choose. One capability per run.

**Steps**

1. **Pick a capability.** If none given, survey the codebase and propose a candidate
   capability list (e.g. `scheduling-core`, `teacher-allocation`, `cache-refresh`), then
   ask which ONE to document (AskUserQuestion). Do NOT auto-document the whole system in
   one pass — one at a time, user-directed.

2. **Guard.** If `specs/<capability>/` already exists, stop: it's baselined; changes to it
   go through `/change-new`, not here.

3. **Ground in the code.** Read the actual functions implementing this capability. Load
   `grill-me`. Walk the spec template's slots, answering from the CODE wherever a question
   can be — grill the USER only for intent/rationale the code cannot reveal. Prove
   behaviour with real references (function names, observed logic), same standard as an
   investigation.

4. **Confirm — the review gate.** Echo back the derived requirements and their scenarios
   (GIVEN/WHEN/THEN describing CURRENT behaviour) plus the C4 view, and get sign-off
   (AskUserQuestion: Confirm / Adjust). Durable truth must be reviewed before it's written.

5. **Write the durable layer.**
   - `specs/<capability>/spec.md` — under `## ADDED Requirements`, with `### Requirement:`
     and `#### Scenario:` (GIVEN/WHEN/THEN, observable outcomes) describing today's behaviour.
   - `specs/<capability>/diagram.md` — C4 container/component view (`c4-diagrams` skill).
   - `specs/README.md` — add this capability to the index and the C4 context diagram.

6. **Seed ADRs from decisions already in the code.** Identify durable architectural
   decisions the codebase already embodies (e.g. a solver choice, a cache-before-blame
   discipline). For each that clears the ADR bar, create `adr/NNNN-kebab-title.md`
   (MADR-short: Context / Decision / Consequences), numbering from 0001 up. Grill the USER
   for the rationale the code can't show; if the "why" is unrecoverable, state that
   explicitly in Context — never fabricate it. Don't invent decisions that don't clear the
   bar. From now on these ADRs are immutable — future changes supersede, never edit.

7. **Stop.** Report what was seeded and which candidate capabilities remain un-baselined.
   Re-run for the next one.

**Guardrails**
- Describe reality, proven by reading code — never assumption or aspiration. Code wins ties.
- Everything is `ADDED` — baseline is the first appearance of each capability.
- One capability per run; skip any already in `specs/`.
- Read-only with respect to CODE — baseline documents, it never edits the codebase.
- This is the ONLY command that writes durable `specs/`—`adr/` directly. After baseline,
  modify the durable layer solely via the change flow and its archive step.
- Confirm each capability with the user before writing (the review gate).
- Don't fabricate ADR rationale; mark unrecoverable "why" as unknown.
- Commit after each capability (e.g. `baseline: <capability>`); tag `base/<capability>` if
  you want a rollback anchor.
