Windows Foundation
==================

Basic installation of a fresh AWS Windows Server instance.

Requirements
------------

AWS Windows Server instance.

Role Variables
--------------

none

Dependencies
------------

This role depends on the following roles:

- windows_common

Example Playbook
----------------

    - hosts: servers
      roles:
         - windows_foundation

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
