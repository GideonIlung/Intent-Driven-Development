---
description: Start a read-only review of existing code.
argument-hint: <slug> <entry-point|path>
---
start review: $ARGUMENTS

1. scripts/idd init review <slug>.
2. scripts/idd extract <path> → nodes + call graph draft. zero token.
3. scripts/idd render <slug> --overview. tell human box count.
4. >9 box → ask human: which entry point, how many hop.
5. write report.md ## Scope.
6. stop. tell human: /review-continue.
