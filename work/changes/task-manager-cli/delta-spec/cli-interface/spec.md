## ADDED Requirements

### Requirement: Command structure

#### Scenario: Basic command invocation
- GIVEN the tool is installed and available as `tm`
- WHEN the user runs `tm add "task title"`
- THEN the command is parsed and executed

#### Scenario: Subcommands with arguments
- GIVEN various task operations exist
- WHEN the user runs `tm <subcommand> <args>`
- THEN the appropriate operation is executed with the provided arguments

### Requirement: Argument parsing

#### Scenario: Parse optional flags
- GIVEN the add command supports optional flags
- WHEN the user runs `tm add "title" --description "desc"`
- THEN the parser correctly identifies and passes both title and description

#### Scenario: Parse status filter
- GIVEN the list command supports status filtering
- WHEN the user runs `tm list --status complete`
- THEN only the specified status filter is applied

### Requirement: Help and usage

#### Scenario: Display help for main command
- GIVEN the user needs command documentation
- WHEN the user runs `tm help` or `tm --help`
- THEN a usage guide is displayed listing all available commands

#### Scenario: Display help for subcommand
- GIVEN the user runs an invalid command
- WHEN the tool detects the error
- THEN a brief error message and relevant help text are shown

### Requirement: Error handling

#### Scenario: Missing required arguments
- GIVEN a command requires arguments
- WHEN the user runs the command without required arguments
- THEN an error is shown with usage information

#### Scenario: Invalid subcommand
- GIVEN the user runs an unknown subcommand
- WHEN the tool parses the input
- THEN an error message is shown with available commands

#### Scenario: Invalid status value
- GIVEN the status command expects one of five valid statuses
- WHEN the user runs `tm status 1 invalid`
- THEN an error is shown listing valid statuses (todo, inprogress, complete, blocked, archived)
