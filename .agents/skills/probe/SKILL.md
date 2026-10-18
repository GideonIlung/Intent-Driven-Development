---
name: probe
description: Run a sandbox probe to prove or refute a claim about existing code. Use in review and investigate whenever a scenario, call or hypothesis needs evidence.
---
# probe

claim no proof = guess. probe = proof.

- one probe = one claim. write claim first.
- file: <work-folder>/probes/<n>-<name>.<ext>. call real code. no edit source.
- run. output → probes/out/.
- record in report: claim, probe file, CONFIRM / REFUTE, one-line evidence.
- REFUTE → fix pseudo or scenario. not code.
- no network. no prod data. fixture only.
- probe >60s → ask human first.
