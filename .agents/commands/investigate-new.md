---
description: Start a bug investigation. Pin the symptom as a failing scenario.
argument-hint: <slug> <symptom>
---
start investigate: $ARGUMENTS

1. scripts/idd init investigate <slug>.
2. skill grill. pin: expected vs actual, when start, how reproduce.
3. skill scenarios → @X failing scenario. concrete value.
4. scripts/idd slice <slug> --from <entry box>.
5. stop. tell human: /investigate-continue.
