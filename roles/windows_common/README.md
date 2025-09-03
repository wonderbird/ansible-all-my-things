Role Name
=========

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

    - name: Run tasks/other.yaml instead of 'main'
      ansible.builtin.include_role:
        name: myrole
        tasks_from: other

See also: https://docs.ansible.com/ansible/latest/collections/ansible/builtin/include_role_module.html

License
-------

MIT

Author Information
------------------

Stefan Boos <kontakt@boos.systems>
