# todo-add

## ADDED
```pascal pseudo
procedure CLI.ADD(title)                         // @A
  task ← TASKS.ADD(title)                        // @A
  return task                                   // @A
end procedure
```

```pascal pseudo
procedure CLI.LIST()                             // @B
  tasks ← TASKS.LIST_OUTSTANDING()               // @B
  return tasks                                  // @B
end procedure
```

```pascal pseudo
procedure CLI.COMPLETE(id)                       // @C
  task ← TASKS.COMPLETE(id)                      // @C
  return task                                   // @C
end procedure
```

```pascal pseudo
procedure CLI.EDIT(id, title)                    // @D
  task ← TASKS.EDIT(id, title)                   // @D
  return task                                   // @D
end procedure
```

```pascal pseudo
procedure CLI.DELETE(id)                         // @E
  TASKS.DELETE(id)                               // @E
  return id                                     // @E
end procedure
```

```pascal pseudo
procedure TASKS.ADD(title)                       // @A
  task ← STORE.CREATE(title)                     // @A
  return task                                   // @A
end procedure
```

```pascal pseudo
procedure TASKS.LIST_OUTSTANDING()               // @B
  tasks ← STORE.READ_OUTSTANDING()               // @B
  return tasks                                  // @B
end procedure
```

```pascal pseudo
procedure TASKS.COMPLETE(id)                     // @C
  task ← STORE.MARK_COMPLETE(id)                 // @C
  return task                                   // @C
end procedure
```

```pascal pseudo
procedure TASKS.EDIT(id, title)                  // @D
  task ← STORE.UPDATE_TEXT(id, title)            // @D
  return task                                   // @D
end procedure
```

```pascal pseudo
procedure TASKS.DELETE(id)                       // @E
  STORE.REMOVE(id)                               // @E
  return id                                     // @E
end procedure
```

```pascal pseudo
procedure STORE.CREATE(title)                    // @A
  task ← { id: next, text: title, complete: no } // @A
  persist task locally                           // @A
  return task                                   // @A
end procedure
```

```pascal pseudo
procedure STORE.READ_OUTSTANDING()               // @B
  tasks ← locally saved incomplete tasks         // @B
  return tasks                                  // @B
end procedure
```

```pascal pseudo
procedure STORE.MARK_COMPLETE(id)                // @C
  task ← locally saved task with id              // @C
  task.complete ← yes                            // @C
  persist task locally                           // @C
  return task                                   // @C
end procedure
```

```pascal pseudo
procedure STORE.UPDATE_TEXT(id, title)           // @D
  task ← locally saved task with id              // @D
  task.text ← title                              // @D
  persist task locally                           // @D
  return task                                   // @D
end procedure
```

```pascal pseudo
procedure STORE.REMOVE(id)                       // @E
  remove locally saved task with id              // @E
  return id                                     // @E
end procedure
```

## MODIFIED

## REMOVED
