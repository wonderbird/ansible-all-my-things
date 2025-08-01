# Only the user can run ansible commands

You MUST NEVER run commands starting with `ansible`, `vagrant`, `docker`, `aws`, `hcloud` yourself. Instead you MUST ask the user for executing such commands when neccessary. Then you MUST wait for the user's response before drawing conclusions or asking for running the next command.
