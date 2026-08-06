---
description: Coherence lint for one change/review. Two read-only checks on the diagram document — (1) Gherkin scenarios vs the exploded System diagram, (2) the exploded System diagram vs the layered Overview+detail views (1-1). Prints to chat; writes nothing.
---

Two coherence checks on a change's or review's diagram document. Both read-only, both
report-and-stop. Executes nothing.
- **Check 1 — behaviour vs structure**: every Gherkin scenario lands on the exploded
  `## System diagram`.
- **Check 2 — diagram vs diagram (1-1)**: the exploded `## System diagram` and the layered
  `## Overview` + detail sections are the same graph.

**Input**: `/trace-check <slug> [check]` — `check` is `scenarios` | `diagrams` | `all`
(default `all`). If no slug, list `work/changes/*/` and `work/reviews/*/` and ask.

**Locate inputs**
- The diagram document (following `templates/diagram.md`): must contain `## System diagram`,
  `## Overview`, and one detail section per Overview box.
- The Gherkin scenarios (delta-spec for a change, review scenarios for a review).
- If a required input is missing, stop and say which. Diagrams must be Mermaid to parse.

---

## Check 1 — scenarios vs System diagram
1. Build an inventory from `## System diagram`: components (nodes), connections (edges,
   with direction), external inputs/outputs.
2. Trace each scenario across it, step by step:
   - GIVEN -> a component/input that establishes the state?
   - WHEN -> a component that receives the event, with a path to it?
   - THEN -> a component that produces/checks the outcome, reachable along the flow?
3. Classify each miss: **missing component** / **unrouted input** / **unowned outcome** /
   **orphan component** (a node no scenario exercises).

## Check 2 — System diagram vs layered (1-1)
1. Parse nodes + edges of `## System diagram`.
2. Parse nodes + edges of `## Overview` and every detail section.
3. Compare both directions and classify:
   - **Node orphan (no detail)** — node in System diagram absent from the layered view.
   - **Node drift** — node in the layered view absent from System diagram.
   - **Edge missing** — edge in System diagram not represented anywhere in the layered view
     (as an Overview edge, a detail-internal edge, or a boundary edge).
   - **Edge drift** — edge in the layered view absent from System diagram.
   - **Boundary mismatch** — a detail section's in/out arrows differ from that box's arrows
     in the Overview.

---

**Two-way resolution**: a finding names a disagreement, not a culprit. Report the
disagreement and BOTH fixes; never pick which side is wrong.

**Output** (to chat, no file):
```
trace-check - <slug>

Check 1 - scenarios vs System diagram
  PASS <capability> / <scenario>
  HOLE <capability> / <scenario>
      WHEN "<step>" -> unrouted input: availability reaches no component
        fix: add it to the System diagram, OR drop the assumption

Check 2 - System diagram vs layered (1-1)
  ISSUE node "Validator" -> in System diagram, no detail section
      fix: add a detail section, OR remove it from System diagram
  ISSUE boundary "Cache" -> detail sends to "Solver"; Overview shows no such arrow
      fix: align the Overview arrow, OR the detail section

Summary: Check 1 - <n> passed / <n> holes.  Check 2 - <n> issues.
```

**What it does not do**: structural coherence only — not correctness, not runtime, not
whether the diagram matches the real code. A lint, not a proof. Execution is Cucumber/Ralph
after code; soundness is TLA+/Alloy.

**Guardrails**
- Read-only; prints to chat; writes no file.
- Runs both checks by default; `scenarios` or `diagrams` scopes to one.
- Needs Mermaid diagrams to parse nodes/edges; freeform art degrades to eyeballing — say so.
- Over-report ambiguous cases rather than silently pass.
- Never pick which side is wrong; report both fixes.