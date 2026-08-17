---
name: c4-diagrams
description: Use when explaining existing code architecture, visualizing a system before detailed design, mapping software boundaries, or producing a diagram artifact. Emits ONE diagram document with fixed headings that trace-check reads.
---

# C4 Diagrams

## Overview
Produce ONE diagram document that shows a system as a flat, machine-readable graph AND a
layered, human-readable view of the same graph. The section headings are a FIXED CONTRACT
that other tools (trace-check) depend on — they are NEVER renamed per project or per run.

## Output contract — use these EXACT headings, every run
Emit a single document following `templates/diagram.md`, with these literal headings, in order:

- `## System diagram` — REQUIRED, machine-facing.
  - ONE flat Mermaid graph: every component and every edge in a single graph.
  - Not split across diagrams; not replaced by a context / container / sequence view.
  - trace-check walks Gherkin scenarios across THIS graph — it must be complete and flat.
- `## Overview` — human-facing.
  - One small Mermaid graph of the same system, <= 7-9 boxes (group and push detail down if larger).
  - 2-3 plain-language bullets: what it does.
- `## <Box name>` — one per Overview box, human-facing.
  - Heading = the box's exact name from the Overview.
  - Bullets: Does / Takes in / Sends out, plus a small Mermaid graph of the box's internals.
- `## Flow: <name>` — OPTIONAL, human-facing.
  - A `sequenceDiagram` for one runtime flow, if it adds value.
  - trace-check IGNORES this section; it is never a substitute for `## System diagram`.

DO NOT emit headings like "System Context", "Container View", "Data Flow", or one section
per C4 level. Those names break the contract. Fold C4 thinking INTO the fixed sections:
Overview ~= context/container level; detail sections ~= component level; System diagram =
the flat union of them; Flow = the dynamic view.

## 1-1 rule (exploded <-> layered)
- Every node/edge in `## System diagram` appears in the layered view (Overview or a detail section).
- Every node/edge in the layered view exists in `## System diagram`.
- A detail section's in/out arrows match that box's arrows in the Overview.
Keep `## System diagram` in plain Mermaid so trace-check can parse it.

## Workflow
1. For existing code: inspect entry points, runtime boundaries, integrations, and persistence
   before drawing. Identify language/framework, entry points, major directories, external
   integrations, data stores; label anything unclear as unknown.
2. Build the flat `## System diagram` FIRST — the complete graph.
3. Derive `## Overview` by grouping the flat graph to <= 7-9 boxes; then one detail section per box.
4. Add `## Flow:` only if a runtime sequence answers a real question.
5. End with assumptions (future/incomplete systems) and open questions (uncertain boundaries,
   ownership, data flow).

## Output rules
- Plain Mermaid `flowchart` / `graph` for structure; `sequenceDiagram` for `## Flow:`. No
  C4-specific Mermaid syntax.
- `## System diagram` MUST be Mermaid (trace-check parses it). Prose elsewhere may use ASCII,
  but keep the graphs Mermaid.
- Concrete labels: actor, system, component, database, queue, external service.
- The System diagram is DELIBERATELY flat and complete — that is the machine view, not a
  "mixed-level" mistake.

## Templates
- `templates/diagram.md` (repo templates dir) — the document SHAPE. Fill it.
- `templates.md` (this skill dir) — Mermaid SNIPPETS for individual graphs within sections.
  These are building blocks, NOT output headings.

## Common mistakes
| Mistake | Fix |
| --- | --- |
| Renaming the sections (System Context, Container View, ...) | Use `## System diagram` and `## Overview` verbatim. |
| No single flat graph | `## System diagram` must be one complete, flat graph. |
| A sequence diagram used as the structure | Put it under `## Flow:`; it never replaces the System diagram. |
| Layered view drifts from the flat graph | Keep 1-1; trace-check Check 2 catches drift. |
| Hiding uncertainty | State assumptions and open questions at the end. |
