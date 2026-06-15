---
name: manual-testing
description: >
  Use when the latest feature implementation is ready for manual end-to-end
  testing and you want to verify the implementation with guided instructions.
---
Read and apply "technical coach" skill instructions as knowledge base for
the following manual end-to-end testing procedure.

Implementation of the latest feature is ready for manual end-to-end test.

Walk the user through the end-to-end tests so that they can verify the
implementation.

# Scope

$ARGUMENTS

If scope is unclear, ask about what to test.

# Procedure

Verify the repository clone is prepared on the user's computer.

First give the instructions to configure shell environment variables such
that the commands issued later will not print clutter like debug messages,
ansible cowsay messages etc.

Explain each step, one by one. While doing so, instruct the user which commands
to execute. The user will run the commands and paste back the output.

If problems show up, follow the instructions of the "record-findings"
skill to file issue in beads. Then use the "fix-problem" skill to claim the
issue, move it to in_progress and fix it.

# Constraints

- When you ask questions, ask them one by one, so that the user can focus on
  each.

- Before you start, think hard: Which steps can you execute yourself, so that
  the effort for the user is minimal? Act accordingly.

- Minimize tokens produced by commands issued. Instruct the user to set
  environment variables for the shell session which lead to reduced output for
  used tools. As much as possible use `rtk` and `rtk summary` to save tokens
  printed by commands. Note: `rtk summary` will hide the output of the command -
  if that is required, omit the `summary` argument.

- If you need to use `ansible` or `molecule` commands, always use `rtk ansible`
  or `rtk molecule` instead.

- Whenever possible, combine commands so that the user needs only one copy-paste
  operation for the sequence of commands. Take into account that the user's
  terminal window breaks them after about 90 characters and introduces 2 spaces
  at the beginning of each line. Compensate this in the commands you ask the
  user to run so that they don't need to fix the line breaks and spaces when
  copy-pasting.
