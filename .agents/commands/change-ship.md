---
description: Prepare an implementation change for Ralph. Runs the trace-check gate, builds a human-readable prd.md for your review, then on your OK converts it to prd.json. Does not run Ralph.
argument-hint: <slug>
---

**Argument**: `$ARGUMENTS`

Prepare a change to hand to the Ralph loop. Order: coherence gate → prd.md (your review) →
prd.json. Stops before Ralph — you run `./ralph.sh` yourself, then `/change-finish`.

**Input**: `/change-ship <slug>`. If omitted, list `work/changes/*/` and ask.

**Steps**

1. **Resolve + require inputs.** Locate the change. Require `tasks.md` and at least one
   `delta-spec/<capability>/spec.md` (use design/diagram too if present). If tasks or
   delta-spec are missing, stop — nothing to ship yet; finish drafting with `/change-continue`.

2. **Coherence gate — trace-check.** Run the `/trace-check` procedure against this change.
   If it reports holes, STOP and show them: don't ship a design whose scenarios and diagram
   disagree. Proceed only when clean, or when the user explicitly waives a specific hole.

3. **Build prd.md for review.** Assemble a human-readable PRD at `work/changes/<slug>/prd.md`.
   Default granularity: one **task group** (`## N` in tasks.md) → one story. For each story:
   - `title` — the task-group name
   - `priority` — the group's order (1, 2, …)
   - `tasks` — the `- [ ] N.Y` items in that group (what to do)
   - `acceptanceCriteria` — the Gherkin scenarios from `delta-spec/` this story must satisfy
     (how you know it's done). Map each scenario to the story whose work fulfils it; if a
     scenario spans stories or none fits, FLAG it rather than guess.
   Lay it out so the task→scenario mapping is visible at a glance — that mapping is what the
   user is reviewing.

4. **Review gate.** Tell the user prd.md is ready and ask them to review it (AskUserQuestion:
   Confirm / Adjust). Do NOT convert to JSON until confirmed. This is the "final look before
   shipping" checkpoint — the whole reason prd.md exists.

5. **Convert to prd.json.** On confirmation, emit `prd.json` at the location `ralph.sh` reads
   (beside the script), matching the loop's schema:
   ```json
   {
     "userStories": [
       {
         "id": "<kebab-slug-of-title>",
         "title": "<task group name>",
         "priority": 1,
         "passes": false,
         "acceptanceCriteria": ["<scenario 1>", "<scenario 2>"]
       }
     ]
   }
   ```
   Every `passes` starts `false`. Preserve priority order.

6. **Stop.** Report: prd.md and prd.json written, story count, and next steps —
   "review prd.json if you like, run `./ralph.sh`, then `/change-finish <slug>` once green."

**Guardrails**
- Do NOT run Ralph and do NOT edit code — preparation only.
- trace-check must pass (or a hole be explicitly waived) before building prd.md.
- prd.md is the review gate: never convert to prd.json until the user confirms.
- Every story's `passes` starts `false`; ground truth is the loop's, not this command's.
- DEFAULT SCHEMA: the block above is inferred from ralph.sh — if the real prd.json keys
  differ, match the real ones.
- DEFAULT GRANULARITY: one task group = one story; change only if the user asks.
