---
description: Resume a read-only investigation — re-grill on what's unresolved or wrong and refine the report. Single document, no dependency chain, no staleness warnings. Never edits code or specs.
argument-hint: [slug]
---

**Argument**: `$ARGUMENTS`

Resume an investigation to dig deeper or fix the report. Unlike a change, an investigation
is ONE document with no dependency chain — so this just re-grills and rewrites the report.
There is no "next artifact" and no warn-and-stop.

**Input**: `/investigate-continue [slug]`. If omitted, list `work/investigations/*/` and ask.

**Steps**

1. **Resolve** the investigation; read its `report.md` and `evidence/`.

2. **Grill on the gap** (load `grill-me`): what in the current report is unproven, unclear,
   or wrong? Interrogate the delta between what's written and what's actually established —
   not empty-slot questions.

3. **Investigate further — read-only.** Trace the open threads to proof, add supporting
   artefacts to `evidence/`, apply the project's checks from `AGENTS.md`. Never guess.

4. **Rewrite `report.md`** with the refined findings, keeping the template structure and
   the chain (cause → change → symptom). Empty sections omitted.

5. **Stop.** Say whether the root cause is now proven. When the report is complete, close it:
   `bash finalise.sh work/investigations/<slug>/report.md` (tags `inv/<slug>` as a read-only
   bookmark). If the investigation concludes a fix is needed, start it with `/change-new` —
   do NOT edit code here.

**Guardrails**
- READ-ONLY. Never edit code, durable `specs/`, or `adr/`.
- No dependency chain, so no staleness warnings — just refine the one report.
- Prove every claim; never guess. Always the chain.
- A fix is a separate `/change-new`.
