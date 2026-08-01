# How this repo works

## Two layers
- `specs/`, `adr/` — DURABLE. What the system does, and why. Append-only.
  `specs/` is kept current by archiving each change. `adr/` is immutable +
  superseding (never edit an accepted ADR; write a new one that Supersedes it).
- `work/` — TRANSIENT. Where documents are authored. Safe to prune once done.

## Two modes
- IMPLEMENTATION → `work/changes/<slug>/`: proposal → specs → design → adr → tasks.
 On completion: archive the change's delta-spec/ into durable specs/
  (stamping `Source: impl/<slug>`), and flatten `tasks.md` → `prd.json` for Ralph.
- INVESTIGATION → `work/investigations/<slug>/`: a `report.md` only. Reads
  `specs/`, never writes it. If it concludes "needs a fix", that becomes a new
  implementation change.

## Templates
In `templates/`. Lead docs (`proposal.md`, `report.md`) carry front-matter:
`type`, `id`, `tag`.

## Git anchors
Finish a document with:  `bash finalise.sh <lead-doc>`
- implementation → tag `impl/<slug>`, roll back with `git revert`
- investigation  → tag `inv/<slug>`, a read-only bookmark (`git checkout`)
List anchors:  `git tag -l 'impl/*'`  /  `git tag -l 'inv/*'`

## Skills
`.agents/skills/`: grill-me, c4-diagrams, gherkin-authoring,
architectural-decision-records, glossary.
