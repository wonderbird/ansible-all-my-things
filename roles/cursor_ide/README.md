Cursor IDE
==========

Provide the Cursor IDE as a Developer's workbench.

Requirements
------------

Linux based computer with apt / dpkg support.

Role Variables
--------------

| Variable | Default | Description |
| --- | --- | --- |
| `login_user_names` | *(required)* | List of local usernames to configure Cursor for. Must contain at least one name; the role fails loudly if it is undefined or empty. |

Dependencies
------------

none

Example Playbook
----------------

    - hosts: servers
      roles:
         - cursor_ide

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
