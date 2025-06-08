Ask clarifying questions if my instructions are unclear.

Repeat my question briefly before responding.

Only the first commit is allowed on the main branch. All other commits require a feature branch. If you are on main, create the feature branch. The name shall follow the pattern: feat/feature-name. The feature name does not contain a category suffix like "docs". If the commit does not address a feature, then ask for clarification.

All commits must use conventional commit prefixes. If the applicable prefix is unclear, then ask.

After completing code changes, commit to git with a conventional message: headline stating new capability (not action taken) + brief description under 50 words (bullet points allowed for readability). Example: use 'feat: show hello message on startup' not 'feat: implement printing hello on startup'.
