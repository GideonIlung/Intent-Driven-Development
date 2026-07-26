---
description: Close out an implementation change AFTER Ralph has passed. Verifies every story passed, reconciles the delta-spec to what was actually built, archives it into durable specs/ (+ ADRs, README), then commits and tags via finalise.sh. Refuses if the build is incomplete.
---

Run this ONCE `ralph.sh` has finished with every story passing. It is the post-build
lifecycle: verify → reconcile → archive → finalise. It does NOT run Ralph (you do that)
and NEVER edits code.

**Input**: `/change-finish <slug>`. If omitted, list `work/changes/*/` and ask.

**Steps**

1. **Resolve the change.**

2. **Verify Ralph succeeded — ground truth, not your say-so.** Read `prd.json` and confirm
   EVERY `userStories[].passes == true`. If any is `false` (or `prd.json` is missing), STOP:
   report how many stories are still failing and that the durable layer was left untouched.
   Never archive a partial build — this mirrors `ralph.sh`'s own stop condition and the
   max-iterations caveat (a loop that ran out of iterations must not archive).

3. **Reconcile the delta-spec to reality.** Ralph can diverge from the plan while building.
   Read the change's commits (`git log` since the change began) and the actual code, and
   compare against the delta-spec's scenarios. Where the built behaviour differs from what
   the delta-spec claims, update the delta-spec so it describes WHAT WAS BUILT — not the
   original plan. If nothing diverged, say so. Archiving an un-reconciled plan would make
   durable `specs/` describe an implementation that doesn't exist.

4. **Archive into the durable layer.**
   - For each `delta-spec/<capability>/spec.md`, MERGE its `ADDED`/`MODIFIED`/`REMOVED`
     deltas into durable `specs/<capability>/spec.md` — never overwrite the living spec.
     `MODIFIED` replaces the full requirement block; `REMOVED` deletes it with its recorded
     reason.
   - Stamp `Source: impl/<slug>` into each durable spec touched, so the map shows which
     change last changed it.
   - Confirm the change's ADRs are present in durable `adr/` (created there during the adr
     step) — confirm, don't duplicate; never edit an existing ADR.
   - Update `specs/README.md` — the capability index and C4 context — to reflect what was
     added/modified/removed.

5. **Finalise.** Run `bash finalise.sh work/changes/<slug>/proposal.md`. Ralph already
   committed the code per-story; this commits the archive edits and tags `impl/<slug>` as
   the completed-change anchor.

6. **Report.** Capabilities archived, ADRs in force, the tag, and the rollback commands
   (`git revert <commit>` / inspect with `git checkout impl/<slug>`). Note that
   `work/changes/<slug>/` may now be pruned — its value lives in `specs/`.

**Guardrails**
- Run only after `ralph.sh` reports success; VERIFY via `prd.json` passes booleans, not a
  claim. Any failing story → stop, durable untouched.
- Never run Ralph, never edit code — post-build lifecycle only.
- Archive reflects WHAT WAS BUILT (reconciled), never the un-reconciled original plan.
- Merge deltas into durable specs; never blindly overwrite the living spec.
- ADRs are immutable — confirm presence, never edit; changes supersede, they don't rewrite.
- If verify or reconcile can't be completed with confidence, stop rather than archive.