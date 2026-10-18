# todo-add

## ADDED
```gherkin
@A
Scenario: Add a task
  Given local tasks are empty [STORE]
  When I run `todo add "Buy milk"` [CLI]
  Then task 1 has the text "Buy milk" [TASKS]
  And task 1 is saved locally [STORE]
```

```gherkin
@B
Scenario: List outstanding tasks
  Given task 1 has the text "Buy milk" and is outstanding [STORE]
  When I run `todo list` [CLI]
  Then I see task 1 with the text "Buy milk" [CLI]
```

```gherkin
@C
Scenario: Complete a task
  Given task 1 has the text "Buy milk" and is outstanding [STORE]
  When I run `todo complete 1` [CLI]
  Then task 1 is marked complete [TASKS]
  And task 1 is saved locally as complete [STORE]
```

```gherkin
@D
Scenario: Edit a task
  Given task 1 has the text "Buy milk" [STORE]
  When I run `todo edit 1 "Buy bread"` [CLI]
  Then task 1 has the text "Buy bread" [TASKS]
  And task 1 is saved locally with the text "Buy bread" [STORE]
```

```gherkin
@E
Scenario: Delete a task
  Given task 1 has the text "Buy milk" [STORE]
  When I run `todo delete 1` [CLI]
  Then task 1 is removed [TASKS]
  And task 1 is no longer saved locally [STORE]
```

## MODIFIED

## REMOVED
