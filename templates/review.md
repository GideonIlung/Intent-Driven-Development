# Review — <subject>

<!-- The deliverable. Written LAST, after the sandbox has run. Front-matter lives on
     scope.md (the lead doc), not here.
     Everything in here is either proven by reading code or proven by execution —
     mark which. Never state a behaviour the sandbox refuted. -->

## Summary
<!-- What this code is for, what it actually does, and how much of that is proven.
     3-5 bullets. Confidence stated plainly. -->

## How it works
<!-- The narrative walk: entry point -> what happens -> what comes out.
     Plain language. Reference node ids so it lines up with the diagram. -->

## Map
<!-- Point at diagrams/system.md. Do NOT duplicate the graph here.
     One line per process group: what it takes in, what it sends out. -->
- `<process>`: takes <input> -> gives <output>

## Scenario results
<!-- Every scenario, its status, and the evidence. This is the spine of the review. -->

| Scenario | Status | Evidence |
| --- | --- | --- |
| `<capability>/<name>` | confirmed | `sandbox/results/<test-id>` |
| `<capability>/<name>` | refuted | expected <x>, observed <y> |
| `<capability>/<name>` | unproven | <what blocked it> |

## Findings
<!-- By severity High -> Medium -> Low; omit empty.
     A finding is a refuted scenario, an uncovered function, an unowned outcome from
     trace-check, or a boundary assumption that turned out false.
     Always the chain: what the code does -> why it differs from the claim -> what it costs.
     A refuted scenario names a DISAGREEMENT, not a culprit — the code may be wrong, or
     the scenario may be. Give both readings; do not pick a side. -->

## Boundary and assumptions
<!-- Which libraries were stubbed and what the stub assumed. A stub that assumed wrong
     invalidates every scenario that ran through it — say which. -->

## Unproven
<!-- What could not be executed and why. Never converted into a claim. -->

## Next
<!-- Concrete follow-ups:
     - fixes -> `/change-new <slug>`
     - confirmed scenarios worth making durable -> `/baseline <capability>`
     - what to review next -->
