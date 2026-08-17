---
type: review
id: <kebab-slug>
tag: rev/<kebab-slug>
commit: <full sha the review is pinned to>
---
## Under review
<!-- The subject in one line. A module, a package, a pipeline, a service. -->

## Entry points
<!-- Where execution starts. File:function per line. This is the root set the
     inventory closure is grown from — get it right or the closure is wrong. -->

## Boundary policy
<!-- Where inspection stops. Default:
     - FIRST-PARTY (source lives in this repo) -> EXPAND. Follow the import, read it,
       put its functions in the System diagram.
     - THIRD-PARTY (installed dependency) -> BOUNDARY. One node in the System diagram,
       its own diagrams/lib-<name>.md, stubbed in the sandbox.
     Record any deviation here with a reason, e.g. a vendored dep treated as first-party,
     or a first-party module too big to expand this run. -->

## Done criteria
<!-- What makes this review finished. Observable, not "understand the code". -->

## Out of scope
<!-- Named, so the closure has a floor. -->

## Sandbox constraints
<!-- Anything that cannot be executed even in a copy: live DB, paid API, GPU,
     licensed solver. These become `unproven`, never guessed. -->
