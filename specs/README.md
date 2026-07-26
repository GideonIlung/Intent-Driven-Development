# System specs — overview

The living map of what the system does. Kept current by the archive step of
every implementation change. Investigations never write here.

## Context
```mermaid
graph TD
  Sheet[Enrolment sheet] --> Cache[Cache builder]
  Cache --> Scheduler[Scheduler · HiGHS/Gurobi]
  Scheduler --> Bundle[Bundle]
  Bundle --> Validator[hisched::validate]
```

## Capabilities
| Capability | What it does | Spec | Diagram |
|------------|--------------|------|---------|
| _(none yet — seeded as changes ADD them)_ | | | |
