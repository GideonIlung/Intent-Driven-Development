---
description: Start a read-only investigation — grill to scope the symptom, scaffold the investigation folder, trace to a proven root cause, and write the report. Never edits code or specs.
argument-hint: [slug|description]
---

**Argument**: `$ARGUMENTS`

Start an investigation: read-only root-cause analysis that ends in a report. It reads the
code and durable `specs/` to ground itself and NEVER edits anything — not code, not
`specs/`, not `adr/`. If it concludes a fix is needed, that becomes a new `/change-new`,
not an edit here.

**Input**: `/investigate-new [slug|description]`. If absent, ask what to investigate.

**Steps**

1. **Get the symptom.** If no input, ask (AskUserQuestion, open): "What's the symptom you
   want investigated?" Derive a kebab-case slug.

2. **Guard.** If `work/investigations/<slug>/` exists, stop and offer
   `/investigate-continue <slug>`.

3. **Grill to scope** (load `grill-me`, walk the report template's frame):
   - the symptom, pinned to a REAL example (an observed failure, a concrete value) — not a vibe
   - what would count as "root cause found" (the done-criteria)
   - what is in and out of scope
   Answer from the CODE and `specs/` wherever you can; grill the user only for intent the
   code can't reveal.

4. **Scaffold** `work/investigations/<slug>/`:
   - `report.md` from `templates/report.md`, with front-matter:
     ```
     ---
     type: investigation
     id: <slug>
     tag: inv/<slug>
     ---
     ```
   - `evidence/` and `diagrams/` directories.

5. **Investigate — read-only.** Trace the chain from symptom to a PROVEN root cause:
   bad input / code path → what it changed → the final symptom. Prove every claim with a
   real example (function name, row value, check result); gather supporting artefacts into
   `evidence/`. Apply the project's investigation discipline from `AGENTS.md` (its
   verification/quality checks). If a claim can't be proven, say so plainly — never guess.

6. **Write `report.md`** per the template: Summary (symptom, most likely source,
   confidence) → Findings (by severity, empty sections omitted) → Checks completed →
   Final answer (root cause + next thing to review). State the CHAIN, never just the symptom.

7. **Stop.** Report where the file is, then: refine with `/investigate-continue <slug>`, or
   close it with `bash finalise.sh work/investigations/<slug>/report.md`.

**Guardrails**
- READ-ONLY. Never edit code, durable `specs/`, or `adr/` — even mid-investigation.
- Prove every claim with a real example; if unprovable, say so. Never guess.
- Always the chain (cause → change → symptom), never just the symptom.
- A fix is a separate `/change-new`, never an edit here.
- Template hints are guidance for you, not content for the report.
