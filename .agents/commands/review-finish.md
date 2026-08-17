---
description: Close out a review AFTER the sandbox has run. Reconciles the description to what execution actually showed, writes review.md, then commits and tags rev/<slug> via finalise.sh. Never writes durable specs/ — hands confirmed scenarios to /baseline instead.
argument-hint: <slug>
---

**Argument**: `$ARGUMENTS`

Run this once `/review-sandbox` has executed. Verify → reconcile → write → finalise.
It NEVER edits code and NEVER writes durable `specs/` or `adr/`.

**Input**: `/review-finish <slug>`. If omitted, list `work/reviews/*/` and ask.

**Steps**

1. **Resolve the review.**

2. **Verify the sandbox ran — ground truth, not your say-so.** Read
   `sandbox/results.md` and confirm every scenario carries a status. If any is still
   `@claimed`, STOP: an unexecuted claim is not a finding. Report which, and that nothing
   was written. The user may waive a specific scenario as deliberately `unproven` — a
   waiver is recorded in `review.md`, never assumed.

3. **Confirm the pin still holds.** Compare `scope.md`'s `commit` with the code the review
   describes. If the working tree has moved on, that is fine — the review describes the
   pinned commit and says so. If artifacts were drafted against a DIFFERENT commit than the
   sandbox ran, STOP: the description and the evidence are not about the same code.

4. **Reconcile the description to what execution showed.** The drafted artifacts describe
   what the code appeared to do; the sandbox says what it does. Where they disagree:
   - update `functions.md` where a signature, return, or side effect proved wrong
   - update `diagrams/system.md` where an edge did not carry what it claimed, or a call
     never happened. Re-run `/trace-check` after any diagram edit.
   - leave the refuted SCENARIO in place, tagged `@refuted` — it is the finding. Do not
     quietly rewrite a scenario to match the code; that erases the disagreement.

5. **Write `review.md`** from `templates/review.md`: Summary → How it works → Map →
   Scenario results → Findings → Boundary and assumptions → Unproven → Next.
   - Every behaviour stated is marked as read-proven or execution-proven.
   - Findings carry the chain: what the code does → why it differs from the claim → what it
     costs. Both readings of every refutation.
   - Stub assumptions that were in force are listed with the scenarios they gate.

6. **Finalise.** Run `bash finalise.sh work/reviews/<slug>/scope.md` — commits the review
   artifacts and tags `rev/<slug>` as a read-only bookmark (`git checkout rev/<slug>`).

7. **Hand off. A review never writes durable truth itself.**
   - Refutations and other High findings → propose `/change-new <slug>` per fix, with the
     capability list the review already implies.
   - Confirmed scenarios for a capability with no entry in `specs/` → propose
     `/baseline <capability>`. Say plainly which are confirmed by execution; those are the
     only ones worth seeding durable truth from.
   - Anything `unproven` that matters → propose `/investigate-new <slug>`.

8. **Report.** The three counts, the tag, the follow-up commands, and that
   `work/reviews/<slug>/sandbox/tree/` and `env/` can be pruned
   (`git worktree remove`) — their value lives in `results.md` and `review.md`.

**Guardrails**
- Run only after `/review-sandbox`; VERIFY via `results.md` statuses, not a claim.
- NEVER write durable `specs/` or `adr/` — review is read-only on the durable layer, like
  an investigation. `/baseline` is the only path from a review to durable truth, and it
  runs separately with its own confirmation gate.
- Never edit code. Never fix what the review found.
- Reconcile the DESCRIPTION to execution; never reconcile a refuted scenario away.
- Refutations name a disagreement, not a culprit — both readings, no side picked.
- If verify or reconcile can't be completed with confidence, stop rather than publish.
