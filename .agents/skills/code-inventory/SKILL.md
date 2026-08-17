---
name: code-inventory
description: Use when mapping what code a unit actually depends on — resolving imports, growing a dependency closure from entry points, deciding what to read into and what to treat as a black box, or listing the surface used from a third-party library. Use for review mode's inventory step and before drawing any diagram of existing code.
---

# Code Inventory

## Overview
Grow a dependency closure from a set of entry points and split every edge into two piles:
code you READ INTO, and code you STOP AT. The split is the whole point — it decides what
appears in the System diagram, what gets a function entry, and what gets stubbed in the
sandbox. Get it wrong and every downstream artifact is wrong.

## The rule
- **First-party** — the source lives in this repo. **EXPAND.** Open the file, read the
  functions, follow ITS imports too. Its functions become nodes in the System diagram.
- **Third-party** — an installed dependency. **BOUNDARY.** One node in the System diagram,
  its own `diagrams/lib-<name>.md`, a stub in the sandbox. Never exploded.

"In this repo" means the file is tracked at the pinned commit. Not "written by us", not
"looks internal" — tracked. Vendored dependencies and generated code are the ambiguous
cases; the scope document's boundary policy decides them, and records why.

## Growing the closure
1. Start from the entry points. This is the root set — nothing enters the closure that is
   not reachable from it.
2. For each module in the frontier, list every import.
3. Classify each import first-party / third-party / unresolved.
4. First-party → add to the frontier. Third-party → record in the boundary table with the
   symbols actually touched. Unresolved → record as unresolved.
5. Repeat until the frontier is empty, or the scope's declared cut-off is reached.
6. Record where you stopped and why. A silently truncated closure looks identical to a
   complete one.

## Surface, not library
For a boundary library, record ONLY the symbols this code touches — the functions, classes
and constants actually referenced. Never the library's whole API. The surface is what the
lib diagram documents and what a stub would have to implement; anything wider is noise and
anything narrower breaks the sandbox.

## Understanding the surface — never guess, and never stop at the name
Recording that `dplyr::left_join` is used is not the same as knowing what it does with your
inputs. Work the ladder, top rung first, and record which rung each entry was settled on.

1. **Signature and docs, in the pinned environment.** Not your local version — the one in
   `inventory.md`. A doc read against the wrong version is worse than no read.
   | Ecosystem | Signature | Docs | Body |
   | --- | --- | --- | --- |
   | R | `args(fn)` · `formals(fn)` | `?fn` · `help(fn, package = "pkg")` | print `fn` · `getAnywhere(fn)` · `methods(fn)` for S3/S4 |
   | Python | `inspect.signature(fn)` | `help(fn)` · `fn.__doc__` | `inspect.getsource(fn)` · the installed file in `site-packages` |
   Confirm the version you read against: `packageVersion("pkg")` /
   `importlib.metadata.version("pkg")`.

2. **Read the installed source when the docs are thin or the behaviour matters.** It is on
   disk. For a boundary library you are not expanding it into the diagram — but reading it to
   settle one question is always allowed and usually faster than arguing about it.

3. **Characterisation probe — the only primary evidence.** Call the real function in the
   sandbox with the ACTUAL inputs this code passes it, and record what comes back. Docs drift,
   docs lie, and docs describe the general case rather than your case. A recorded real call
   does not. This is what the stub's fixture is built from — see `sandbox-probe`.

4. **Unresolved.** If none of the above can settle it, say so, and every scenario that
   depends on the behaviour is `unproven`. Never a guess dressed as a surface entry.

Docs are secondary evidence. A probe beats a doc; a doc beats a memory; a memory is not
evidence at all.

## Execution treatment is a SEPARATE decision
Boundary means "not exploded into the System diagram". It does NOT mean "stubbed". Fill the
inventory's treatment column on this test:

| Treatment | When | Examples |
| --- | --- | --- |
| **real** | pure, deterministic, cheap, no external state. The default. | dplyr, data.table, numpy, pandas, jsonlite, stringr, stdlib |
| **stub** | side effects or an external dependency: network, DB, filesystem outside a temp dir, clock, randomness, credentials, a licence check | DBI/odbc, httr/requests, boto3, a solver behind a licence |
| **unavailable** | cannot be run even stubbed — see `scope.md`'s sandbox constraints | a paid API with no sandbox tier, GPU-only code |

Prefer `real` whenever it is defensible. A real call cannot be wrong about the library; a
stub always can. Reach for `stub` because of an EFFECT you must not cause, never because
faking it is more convenient.

## Unresolved is a status, not a failure
Dynamic imports, conditional imports, reflection, plugin registries, generated modules, a
path that does not exist at the pinned commit. Record them as unresolved with what you saw.
Never guess a side. An unresolved import that turns out to be first-party is a hole in the
diagram; one guessed as third-party gets stubbed and the stub lies.

## Resolution notes by ecosystem
| Ecosystem | First-party signal | Boundary signal |
| --- | --- | --- |
| Python | relative import; absolute import resolving to a tracked path | installed distribution; stdlib |
| R | `source()` of a tracked file; a function defined in this package | `library()` / `::` on an installed package |
| JS/TS | relative or path-aliased import resolving to a tracked file | bare specifier resolving into `node_modules` |
| Go | package path under this module | any other module path |

Stdlib is a boundary library, but it is usually run REAL rather than stubbed — record it in
the boundary table with `real` as its sandbox treatment.

## Output
Fill `templates/inventory.md`: the expanded table, the boundary table, unresolved, and the
closure notes (root set size, counts, where expansion stopped).

## Common mistakes
| Mistake | Fix |
| --- | --- |
| Expanding into a third-party library because the code was interesting | Boundary means boundary. Its own diagram, one node. |
| Listing a library's full API as the surface | Only the symbols actually referenced. |
| Guessing a dynamic import onto a side | List it under Unresolved. |
| Closure grown from files rather than from entry points | Start at the root set; reachability is the filter. |
| Stopping early without saying so | Record the cut-off and its reason in closure notes. |
| Classifying by name or vibe | Classify by whether the file is tracked at the pinned commit. |
| Recording a surface entry without knowing what it does | Work the evidence ladder; `?fn` at minimum. |
| Marking a pure library `stub` | `real` is the default; stub only for effects. |
| Treating boundary as implying stubbed | Two separate decisions. Fill the treatment column deliberately. |