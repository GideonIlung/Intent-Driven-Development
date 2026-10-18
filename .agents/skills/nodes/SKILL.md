---
name: nodes
description: Write nodes table, the boxes of the system diagram. Use whenever adding, changing or removing components or files in nodes.md, or when pseudo code calls an unknown box.
---
# nodes

file: nodes.md. one markdown table.

| ID | shape | label | file |
|---|---|---|---|
| CLI | entry | cli | src/todo/cli.py |
| SVC | op | task service | src/todo/svc.py |
| VAL | cond | title check | src/todo/val.py |
| STORE | store | tasks.json | src/todo/store.py |

shape (only these):
- entry: scenario start
- op: do work
- cond: decide / check
- store: hold data
- file: file artefact

rule:
- ID UPPERCASE. unique in capability.
- no arrow. arrow come from pseudo call.
- file = where box live. empty ok → extract fill.
- box no procedure + nobody call = orphan = error.
- >9 box touched → split change.
- change: row under ## ADDED / ## MODIFIED / ## REMOVED.
