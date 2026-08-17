---
description: Start a code review — grill to scope the subject, pin the commit, agree the boundary policy, scaffold the review folder. Reads code and runs it in a sandbox; never edits the working tree. Does not draft the rest of the chain.
argument-hint: <slug|description>
---

**Argument**: `$ARGUMENTS`

Start a review: describe what code ACTUALLY does, then falsify that description by
running it. It reads the repo and durable `specs/` to ground itself, and executes code
ONLY inside a throwaway sandbox. It NEVER edits the working tree, `specs/`, or `adr/`.
A fix is a new `/change-new`.

This ONLY produces `scope.md` and the folder — it stops before the chain. Run
`/review-continue` for the next artifact.

**Where review sits**
- `/change-*` — what SHOULD be true. Builds it.
- `/investigate-*` — why ONE thing is broken. Proves one chain.
- `/review-*` — what IS true across a whole unit. Describes it, then executes to check.
- `/baseline` — writes durable truth. A finished review is good input to it; a review
  never writes durable `specs/` itself.

**Input**: `/review-new [slug|description]`. If absent, ask what to review.

**Steps**

1. **Get the subject.** If no input, use AskUserQuestion (open): "What code do you want
   reviewed?" Derive a kebab-case slug.

2. **Guard.** If `work/reviews/<slug>/` exists, stop and offer `/review-continue <slug>`.

3. **Pin the commit.** Record `git rev-parse HEAD`. Every later artifact and the sandbox
   read THIS sha. A review of a moving tree proves nothing.

4. **Grill to scope** (load `grill-me`, walk `templates/scope.md`'s slots):
   - the subject, and the **entry points** — file:function, the root set the closure grows
     from. Push hardest here: a wrong root set produces a wrong inventory, which poisons
     the diagram, the scenarios and the sandbox.
   - the **boundary policy** — where inspection stops. Propose the default and get it
     confirmed:
     - first-party (source in this repo) → EXPAND: follow the import, read it, its
       functions become nodes in the System diagram.
     - third-party (installed dependency) → BOUNDARY: one node, its own
       `diagrams/lib-<name>.md`, stubbed in the sandbox.
     Capture any deviation with its reason (vendored deps, a first-party module too large
     to expand this run).
   - **done criteria** — observable, not "understand the code".
   - **out of scope**, and **sandbox constraints** (what cannot be executed even in a copy).
   Answer from the CODE wherever you can; grill the user only for intent the code can't reveal.

5. **Confirm structure — the checkpoint.** Before writing, echo back and get sign-off
   (AskUserQuestion: Confirm / Adjust):
   - the entry points
   - the boundary policy, with the first-pass split of what will expand vs stay a boundary
   - the rough process groups you expect in the Overview
   Do NOT scaffold until confirmed.

6. **Scaffold `work/reviews/<slug>/`.**
   - `scope.md` from `templates/scope.md`, filled, with front-matter:
     ```
     ---
     type: review
     id: <slug>
     tag: rev/<slug>
     commit: <sha>
     ---
     ```
   - Create empty `diagrams/`, `scenarios/`, `sandbox/`, `evidence/`.
   - Do NOT write inventory.md, functions.md, scenarios, or review.md.

7. **Stop.** Report what was created, then:
   "Run `/review-continue <slug>` to draft the next artifact (inventory)."

**Guardrails**
- Produce ONLY `scope.md` + the folder scaffold. Never advance the chain here.
- Pin the commit at scope time; never re-pin silently mid-review.
- READ-ONLY on the working tree, durable `specs/`, and `adr/` — always. Execution happens
  only in `/review-sandbox`, only against a copy.
- Entry points and boundary policy must be user-confirmed before scaffolding.
- Template `<!-- comments -->` are guidance for you; never leave them in the output.
- If the slug exists, defer to `/review-continue`.
