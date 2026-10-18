---
name: pseudo
description: Write algorithmic pseudo code with path tags. Use whenever writing or editing pseudo.md, designing procedures for a change, or describing existing code in review or investigate.
---
# pseudo

file: pseudo.md. one procedure per block. fence = ```pascal pseudo

```pascal pseudo
procedure SVC.ADD(title)              // @A @B
  ensures valid → STORE has +1 task   // @A
  ensures empty → STORE unchanged     // @B
  if not VAL.CHECK(title) then        // @A @B
    return "Title required"           // @B
  end if
  id ← STORE.SAVE(title)              // @A
  return "Added #" ‖ id               // @A
end procedure
```

keyword: procedure if then else for each while do return not and or requires ensures. block end: end if / end for / end while / end procedure.
assign ←. concat ‖.

rule:
- name = BOX.METHOD. BOX in nodes.
- call other box = BOX.METHOD(...). this = arrow. no hidden call.
- tag every line // @X for each scenario that run it.
- block end line no tag. inherit.
- untagged line = uncovered = error.
- ensures optional. use when Then-step need it.
- logic only. no lib name. no real-lang syntax.
- ≤ ~15 line per procedure. longer → split.
- change: under ## ADDED / ## MODIFIED / ## REMOVED. MODIFIED = full new procedure.
- review: code as is. not as should be.
