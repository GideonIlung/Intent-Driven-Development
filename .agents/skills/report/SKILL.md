---
name: report
description: Write findings report for review or root-cause report for investigate. Use whenever writing report.md or closing a review or investigate step.
---
# report

human read. short bullet. no story.

review report.md:
- ## Scope — entry point, hop, box count
- ## Findings — box, line, what, high/med/low
- ## Unconfirmed — claim not probed
- ## Next — suggest change or nothing

investigate report.md:
- ## Symptom — @X scenario
- ## Path — box → box along @X
- ## Root cause — box, pseudo line, file:line
- ## Evidence — probe + result
- ## Fix sketch — 1-3 bullet. no code
- ## Hand-off — /change-new <slug>-fix --hotfix

rule: finding no evidence → Unconfirmed.
