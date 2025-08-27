AI Agent
========

A brief description of the role goes here.

Requirements
------------

A running Windows server is required.
The Windows server must be provisioned with role "Windows Foundation" first.

Role Variables
--------------

none

Dependencies
------------

Role "Windows Foundation"

Example Playbook
----------------

    - hosts: moria
      roles:
         - windows_foundation
         - ai_agent

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
