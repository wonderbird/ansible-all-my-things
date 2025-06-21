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

All commits must use one of the following conventional commit prefixes: `feat:`, `refactor:`, `docs:`. If the correct prefix is unclear, I ask the user.

The size of my commits is such, that an experienced developer would need about 10 - 30 minutes to create a similar commit.

Every commit is a small coherent and working increment.

The headline of a `feat:` commit explains the new capability of the project in short. The headline of such a commit does not tell what I have done to achieve this. Example: I would write use 'feat: show hello message on startup' instead of 'feat: implement printing hello on startup'.

I only add a brief description of at most 50 words, if the changes were complicated.
