# Cline's collaboration with the user

## Clarify ambiguity before acting

If my instructions are unclear, ambiguous or inconsistent, I describe this situation and ask clarifying questions before proceeding.

## Important principles

**Small increments:** I plan changes such, that every commit represents a working increment. The size of my commits is equivalent to what a human developer would achieve within 15-30 minutes. After at most 2 commits, I ask the user for review.

**Keep it simple:** I must keep modifications, configuration and options at the absolute minimum to achieve the current goal. I focus on simplicity to achieve a high level of maintainability and robustness.

**Work diligently:** I mark only those tasks completed that have been actually verified by the user. If there are multiple tasks, then incomplete tasks must stay in the task list. If the status of a task is unclear, then I ask for clarification.

## Git version control rules

### Git branching strategy

Before modifying any file, I ensure that I am on an appropriate branch. I ask the user if I am unsure.

Only the first commit is allowed on the `main` branch.

All commits after the first require a feature branch.

Feature branches are named `feat/feature-name`. The feature name MUST NOT contain suffixes like "-docs".

The commit resulting from merging a feature branch into `main` is tagged. The tag name follows the pattern `v1` where `1` represents an increasing integer number starting at 1.

### Commit conventions

My commits must use one of the following conventional commit prefixes: `feat:`, `fix:`, `refactor:`, `docs:`. If the correct prefix is unclear, I ask the user.

The size of my commits is such, that an experienced developer would need about 10 - 30 minutes to create a similar commit.

All my commits represent a small, coherent and working increment.

The headline of a `feat:` commit explains the new capability of the project in short. The headline of such a commit does not tell what I have done to achieve this. Example: I would write use "feat: show hello message on startup" instead of "feat: implement printing hello on startup".

The headline of a `fix:` commit describes the most important symptom of the problem in past tense. The commit message body describes the problem and its root cause. It may also contain the major steps required to fix the problem.

The brief description of a commit body shall not exceed 50 words.

### Git command line tool usage

I use the `--no-pager` flag before any other parameter when requesting git history information. This ensures that your git commands don't block forever.

## Code style

**Markdown** must comply with the rules specified by the Visual Studio Code **markdownlint** plugin. These rules are maintained here: https://raw.githubusercontent.com/DavidAnson/markdownlint/refs/heads/main/doc/Rules.md
