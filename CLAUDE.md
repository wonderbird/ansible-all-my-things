# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## How to "follow your custom instructions"

### Understand custom rules and memory bank before following custom instructions

When the user says "follow your custom instructions" for the first time, I do the following:

1. Read all files in the directory `.clinerules/` and the linked files. These files describe custom rules which will be effective from now on. They also describe the memory bank concept.

2. Read all files in the directory `memory-bank/`. These files describe the goals and the context of the current project iteration.

3. Only read additional files if the user agrees. I want to save context tokens at this stage.

After that I summarize what I have learned and what I understand as the next immediate action. Then I ask whether I should now execute the next immediate action.

### Summarize iteration status and next immediate action before following custom instructions

For subsequent "follow your custom instructions" commands I will summarize the current stage of the iteration and the next immediate action.

Then I ask whether I should now execute the next immediate action.

I assume that the user will tell me to "refresh my custom instructions" whenever the related files have changed.
