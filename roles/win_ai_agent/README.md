AI Agent
========

Run AI agents like Claude Code on Windows (incomplete).

Requirements
------------

A running Windows server is required.
The Windows server must be provisioned with role "Windows Foundation" first.

Role Variables
--------------

none

Dependencies
------------

This role depends on the following roles:

- windows_common
- windows_foundation

Example Playbook
----------------

    - hosts: moria
      roles:
         - windows_foundation
         - win_ai_agent

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
