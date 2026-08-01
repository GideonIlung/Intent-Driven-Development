---
description: Resume an implementation change — advance to the next artifact, or revise an existing one (warn-and-stop). Grill-me runs in both branches.
argument-hint: [slug] [artifact]
---

**Argument**: `$ARGUMENTS`

Resume an implementation change. Two branches, chosen automatically:
- ADVANCE (default): draft the next artifact in dependency order.
- REVISE (when you name an artifact that already exists): re-grill and rewrite it,
  then warn about what it invalidated.

The chain and its dependencies:
```
proposal ─┬─► delta-spec ─────► tasks
          └─► design ──► adr ──► tasks
```
delta-spec requires proposal · design requires proposal · adr requires design ·
tasks requires delta-spec AND adr.

**Input**: `/change-continue [slug] [artifact]`
- `slug` — which change. If omitted, infer from context, else list `work/changes/`.
- `artifact` — optional. If named AND it already exists on disk → REVISE. Otherwise → ADVANCE.

**Steps**

1. **Resolve the change.** If no slug, list `work/changes/*/` (most-recent first) and
   ask which with AskUserQuestion.

2. **Read state.** Determine which artifacts are drafted vs missing: `proposal.md`,
   `delta-spec/` (non-empty?), `design.md`, `adr.md`, `tasks.md`.

3. **Choose branch.** Artifact named AND exists → REVISE. Else → ADVANCE.

---

**ADVANCE**

a. Pick the target: the first artifact whose dependencies are all drafted but which
   isn't written yet, in order delta-spec → design → adr → tasks. (proposal should
   exist from `/change-new`; if not, it's the target — grill it as change-new does.)

b. Load `templates/<artifact>.md`, read the artifact's dependency files for context,
   and load the matching skill:
   - **delta-spec** → `grill-me` + `gherkin-authoring`. One `delta-spec/<capability>/spec.md`
     per capability from the proposal, using OpenSpec delta headers
     (`## ADDED Requirements`, `### Requirement:`, `#### Scenario:` with GIVEN/WHEN/THEN
     observable outcomes).
   - **design** → `grill-me` + `c4-diagrams`. Fill Context / Goals-Non-Goals / Decisions /
     Risks / Migration / Open Questions; put the C4 view in `diagrams/`.
   - **adr** → `architectural-decision-records`. Create a durable `adr/NNNN-*.md` ONLY if a
     decision clears the bar (long-term, affects future changes, not already in force);
     else write `adr.md` stating none. Never edit an existing ADR — supersede it.
   - **tasks** → derive from delta-spec + design + adr. Every task a `- [ ] N.Y` checkbox
     under `## N` groups, dependency-ordered, each small and verifiable.

c. Grill against the template's slots (fill blanks). Apply skill rules as constraints;
   never copy template hints into the output.

d. Write that ONE artifact. Stop. Report what was written and what the next artifact is.

---

**REVISE**

a. Re-open the named artifact. Load `grill-me`. Grill on the GAP — the delta between
   what's written now and what's actually right — not empty-slot questions. Rewrite it.

b. **Warn and stop.** Compute the downstream artifacts (everything that transitively
   depends on the one revised):
   - proposal → delta-spec, design, adr, tasks
   - delta-spec → tasks
   - design → adr, tasks
   - adr → tasks
   - tasks → (none)
   For each downstream artifact that EXISTS on disk, print it as STALE with a one-line
   reason and its repair command (`/change-continue <slug> <artifact>`).
   Then state plainly: durable `specs/` is untouched (nothing archives until finish),
   and `prd.json` is not built yet.
   Do NOT cascade (never auto-rewrite downstream) and do NOT delete anything.

**Guardrails**
- One artifact per invocation — ADVANCE writes one; REVISE rewrites one and warns.
- grill-me runs in BOTH branches: empty slots on advance, the gap on revise.
- REVISE over-warns by design: flag a downstream artifact stale even if the change may
  not affect it. Better a glance than a silent stale doc.
- Never touch durable `specs/`, durable `adr/`, or code — those belong to finish/archive
  and the Ralph loop.
- Template hints are constraints for you, not content for the file.
