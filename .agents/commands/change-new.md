---
description: Start a new implementation change — grill against the proposal, confirm structure, scaffold the change folder. Does not draft the rest of the chain.
argument-hint: <slug|description>
---

**Argument**: `$ARGUMENTS`

Start a new implementation change. This ONLY produces the proposal and scaffolds the
folder — it deliberately stops before the rest of the chain. Run `/change-continue`
to draft the next artifact.

**Input**: the argument after `/change-new` is either a kebab-case slug or a
description of what to build. If absent, ask.

**Steps**

1. **Get intent.** If no input, use the AskUserQuestion tool (open-ended):
   "What change do you want to make? Describe what you want to build or fix."
   Derive a kebab-case slug (e.g. "fix fake teacher repair" → `fix-fake-teacher-repair`).

2. **Guard.** If `work/changes/<slug>/` already exists, stop and ask whether to
   resume it with `/change-continue <slug>` instead. Never overwrite.

3. **Load structure + skill.**
   - Read `templates/proposal.md` — its sections ARE the slots to fill
     (Why, What Changes, Capabilities → New/Modified, Impact).
   - Load the `grill-me` skill.

4. **Grill against the template.** Walk each slot and interrogate until it's pinned —
   questions driven by the template's slots, not generic ones. Push HARDEST on
   Capabilities: each New Capability becomes a `delta-spec/<name>/spec.md` downstream,
   so a wrong capability list poisons the whole chain. Prefer reasonable decisions to
   keep momentum, but NEVER invent the capability list — that comes from the user.

5. **Confirm structure — the checkpoint.** Before writing anything, echo back the
   agreed skeleton and get sign-off with AskUserQuestion (Confirm / Adjust):
   - the capability list, each mapped to the `delta-spec/<name>/spec.md` it will create
   - a rough sketch of the expected task groups
   Do NOT scaffold until the user confirms. This is the "same page on structure" gate.

6. **Scaffold `work/changes/<slug>/`.**
   - Write `proposal.md` from `templates/proposal.md`, filled with the grilled answers,
     with front-matter:
     ```
     ---
     type: implementation
     id: <slug>
     tag: impl/<slug>
     ---
     ```
   - Create empty `delta-spec/` and `diagrams/` directories.
   - Do NOT write design.md, adr.md, or tasks.md.

7. **Stop.** Report what was created, then:
   "Run `/change-continue <slug>` to draft the next artifact (delta-spec)."

**Guardrails**
- Produce ONLY the proposal + folder scaffold. Never advance the chain here.
- Template `<!-- comments -->` are guidance for you — fill sections with real content;
  never leave the hint comments in the output.
- The capability list must be user-confirmed at the checkpoint before scaffolding.
- Never touch durable `specs/`, `adr/`, or code.
- If the slug already exists, defer to `/change-continue`.
