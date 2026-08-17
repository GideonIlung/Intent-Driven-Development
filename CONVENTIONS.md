# How this repo works

## Two layers
- `specs/`, `adr/` — DURABLE. What the system does, and why. Append-only.
  `specs/` is kept current by archiving each change. `adr/` is immutable +
  superseding (never edit an accepted ADR; write a new one that Supersedes it).
- `work/` — TRANSIENT. Where documents are authored. Safe to prune once done.

## Three modes
- IMPLEMENTATION → `work/changes/<slug>/`: proposal → specs → design → adr → tasks.
 On completion: archive the change's delta-spec/ into durable specs/
  (stamping `Source: impl/<slug>`), and flatten `tasks.md` → `prd.json` for Ralph.
- INVESTIGATION → `work/investigations/<slug>/`: a `report.md` only. Reads
  `specs/`, never writes it. If it concludes "needs a fix", that becomes a new
  implementation change.
- REVIEW → `work/reviews/<slug>/`: scope → inventory → diagrams → functions →
  scenarios → sandbox → review. Describes what EXISTING code does at a pinned commit,
  then executes it in a disposable sandbox to falsify the description. Reads `specs/`,
  never writes it. Findings become new changes; confirmed scenarios feed `/baseline`.

  Which mode: change = what SHOULD be true · investigation = why ONE thing is broken ·
  review = what IS true across a unit · baseline = writing durable truth down.

## Templates
In `templates/`. Lead docs (`proposal.md`, `report.md`, `scope.md`) carry front-matter:
`type`, `id`, `tag`. A review's `scope.md` also carries `commit` — the sha the whole
review is pinned to.

## Git anchors
Finish a document with:  `bash finalise.sh <lead-doc>`
- implementation → tag `impl/<slug>`, roll back with `git revert`
- investigation  → tag `inv/<slug>`, a read-only bookmark (`git checkout`)
- review         → tag `rev/<slug>`, a read-only bookmark (`git checkout`)
List anchors:  `git tag -l 'impl/*'`  /  `git tag -l 'inv/*'`  /  `git tag -l 'rev/*'`

## Skills
`.agents/skills/`: grill-me, c4-diagrams, gherkin-authoring,
architectural-decision-records, glossary, code-inventory, sandbox-probe.

## Code execution
Only two things run code: the Ralph loop (building a change) and `/review-sandbox`
(executing a review's claims against a disposable copy at the pinned commit). Nothing
else executes anything, ever.