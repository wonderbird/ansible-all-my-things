# Cline's collaboration with the user

## Clarify ambiguity before acting

If my instructions are unclear, ambiguous or inconsistent, I describe this situation and ask clarifying questions before proceeding.

## Git version control rules

### Git branching strategy

- Only the first commit is allowed on the `main` branch.
- All commits after the first require a feature branch.
- Feature branches are named `feat/feature-name`. The feature name MUST NOT contain suffixes like "-docs".
- The commit resulting from merging a feature branch into `main` is tagged. The tag name follows the pattern `v1` where `1` represents an increasing integer number starting at 1.

I ask the user whether I shall create a new feature branch, if we are `main` and a file needs to be created or changed.

### Commit conventions

All commits must use one of the following conventional commit prefixes: `feat:`, `fix:`, `refactor:`, `docs:`. If the correct prefix is unclear, I ask the user.

The size of my commits is such, that an experienced developer would need about 10 - 30 minutes to create a similar commit.

Every commit is a small coherent and working increment.

The headline of a `feat:` commit explains the new capability of the project in short. The headline of such a commit does not tell what I have done to achieve this. Example: I would write use "feat: show hello message on startup" instead of "feat: implement printing hello on startup".

The headline of a `fix:` commit describes the most important symptom of the problem in past tense. The commit message body describes the problem and its root cause. It may also contain the major steps required to fix the problem.

The brief description of a commit body shall not exceed 50 words.

### Git command line tool usage

Use the `--no-pager` flag before git commands to ensure that no pager is never to display git history information. This ensures that your git commands don't block forever.

## Code style

**Markdown** must comply with the rules specified by the Visual Studio Code **markdownlint** plugin. These rules are maintained here: https://raw.githubusercontent.com/DavidAnson/markdownlint/refs/heads/main/doc/Rules.md
