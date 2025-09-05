Windows Common
==============

Tasks shared among windows related roles.

Requirements
------------

AWS Windows Server instance.

Role Variables
--------------

none

Dependencies
------------

none

Example Playbook
----------------

To include a task from this role in another role:

    - name: Reboot
      ansible.builtin.include_role:
        name: windows_common
        tasks_from: reboot-if-pending

See also: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_role_module.html

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
