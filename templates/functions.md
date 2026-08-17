# Function reference — <subject>

<!-- One entry per function in the inventory's EXPANDED set. This is the callable
     contract the sandbox is built against — a wrong signature here is a broken test.
     Read the code; do not infer from the name. Node IDs must match the System diagram. -->

## <module path>

### `<name>(<signature>)`
- **Node**: `<System diagram node id>`
- **Does**: <what it is meant to do — one or two bullets, plain language>
- **Takes in**: <each parameter: name, type, meaning, required/default>
- **Gives back**: <return type + meaning. `none` if it returns nothing.>
- **Raises**: <errors it can throw, and on what. `none` if it cannot fail.>
- **Side effects**: <writes, network, globals, mutated arguments. `pure` if none.>
- **Calls**: <first-party functions it calls, by node id · boundary libraries by name>
- **Called by**: <node ids>
- **Scenarios**: <scenario names that exercise it — filled in at the scenarios step>

### `<name>(<signature>)`
- ...

## Coverage
<!-- Filled at the scenarios step. The gap is the finding. -->
- Functions documented: <n>
- Functions with at least one scenario: <n>
- Uncovered: <list — each one is a function no scenario exercises>
