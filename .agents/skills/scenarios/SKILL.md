---
name: scenarios
description: Write Gherkin scenarios with @tags and box tags. Use whenever writing or editing scenarios.md, turning intent into testable behaviour, or inferring behaviour from code in review.
---
# scenarios

file: scenarios.md. one ```gherkin block per scenario.

```gherkin
@A
Scenario: Add valid task
  Given store empty                 [STORE]
  When I run todo add "Milk"        [CLI]
  Then task 1 saved                 [STORE]
  And I see "Added #1"              [CLI]
```

rule:
- one tag per scenario. next free letter.
- every step end [BOX]. box must exist in nodes.
- first When step box = entry shape.
- one behaviour per scenario. happy path + each error path separate.
- concrete value ("Milk", 1). no "some", no "valid data".
- no UI detail. no impl detail.
- change: under ## ADDED / ## MODIFIED / ## REMOVED. MODIFIED keep same tag.
- --refactor: no delta. --hotfix: max 1 scenario.
- after write: scripts/idd trace-check <slug>.
