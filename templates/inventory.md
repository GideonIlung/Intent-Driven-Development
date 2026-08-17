# Inventory — <subject>

<!-- The resolved closure from the entry points, split by the scope's boundary policy.
     This is the unit list every later artifact is built from: diagrams, functions,
     scenarios, sandbox stubs. Nothing appears downstream that is not listed here. -->

## Expanded — first-party
<!-- Source is in this repo. Read it. Its functions become nodes in the System diagram. -->

| Module | Path | Reached from | Why in scope |
| --- | --- | --- | --- |
| `<name>` | `<path>` | `<importer>` | <one line> |

## Boundary — third-party
<!-- Installed dependency. NOT expanded. One node in the System diagram, one
     diagrams/lib-<name>.md of the surface actually used, one stub in the sandbox.
     "Surface used" is only the symbols this code touches — never the whole library. -->

| Library | Version | Surface used | Behaviour settled by | Used for | Treatment |
| --- | --- | --- | --- | --- | --- |
| `<name>` | `<pinned>` | `<fns/classes touched>` | probe / source / docs / unresolved | <one line> | real / stub / unavailable |

<!-- Treatment: `real` is the DEFAULT — pure, deterministic, cheap libraries are run, not
     faked. `stub` only where an effect must not happen (network, DB, filesystem, clock,
     randomness, credentials, licence check). `unavailable` per scope.md's constraints.
     "Behaviour settled by" records how you know what the surface does: a characterisation
     probe (primary evidence), the installed source, the pinned docs (`?fn` / `help(fn)`),
     or unresolved — in which case dependent scenarios are `unproven`. -->

## Unresolved
<!-- Imports that could not be classified: dynamic imports, conditional imports,
     reflection, generated code, a path that does not exist. Say so; never guess a side. -->

## Closure notes
- Root set: <n entry points>
- Expanded: <n modules>, <n functions>
- Boundary: <n libraries>
- Depth reached / cut: <where expansion stopped and why>