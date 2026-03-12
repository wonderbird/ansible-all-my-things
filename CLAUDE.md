# CLAUDE.md

This file provides guidance to coding agents when working with projects in this folder.

## Rules are stored in .specify/memory/constitution.md and in .cursor/rules

This project uses spec-kit for guiding the coding agent. Thus, rules important
for developing the project are stored in `.specify/memory/constitution.md`. This file is the source of truth for the project and must be read and followed carefully.

Rules describing the interaction between the coding agent and the user are stored in the .cursor/rules directory and in contained subdirectories.

If rules conflict, then you MUST ask the user for clarification before proceeding.

## How to follow your custom instructions

Whenever the user says "follow your custom instructions", then you must read .cursor/rules/general/500-cline-memory-bank.mdc.

If there is no memory bank, then you MUST ask the user for clarification before proceeding.

Then read the memory bank and identify the immediate next action.

Afterwards, read the project constitution at `.specify/memory/constitution.md` and verify that your plan complies with each principle.

Then identify the applicable rules and read them.

Finally, confirm readiness as described in .cursor/rules/general/900-confirm-readiness.mdc.

## Git command line tool usage

When requesting git history information, ALWAYS use the `--no-pager` flag as the very first option to git (e.g. `git --no-pager log`). This avoids blocking git commands waiting for the user to terminate the pager.

## LS tool does not show hidden files

When you want to check whether a hidden file or directory exists, then you MUST use a tool native to the operating system you are running on. The LS tool does not handle hidden files.
