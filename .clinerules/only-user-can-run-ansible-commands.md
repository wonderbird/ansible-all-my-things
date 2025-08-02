# Only the user can run ansible commands

You MUST NEVER run commands for one of the following services:

- ansible
- vagrant
- docker
- tart
- aws
- hcloud

Instead you MUST ask the user for executing such commands, if neccessary.

Then you MUST wait for the user's response before drawing conclusions or asking for running the next command.
