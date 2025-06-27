# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Guidelines

Before executing any prompt, I follow these instructions:

- I always read all files in the `.clinerules/` folder and I read the linked files in order to understand the rules and guidelines affecting the chat session.

- I always read the Memory Bank to understand the goals and the context of the current project iteration.

- At this stage of the conversation, I never read other files than linked in the `.clinerules/` folder and in the Memory Bank in order to save context tokens.

- After I have read the `.clinerules/` folder and the Memory Bank, I summarize what I have learned and what I understand as the next immediate action. Then I ask whether I should now execute the next immediate action.

## Custom Commands

The following list shows how I process specific chat messages issued by the user:

| Chat Message                    | My interpretation |
| ------------------------------- | ----------------- |
| follow your custom instructions | Using the files in the `.clinerules/` directory and in the Memory Bank, I identify the next immediate action. I ask the user whether I shall execute it. |
