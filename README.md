# Lookup Plugin - Auto Absent
 
The Auto Absent plugin allows the user to perform a diff of two YAML data structures, and automatically generate a new structure which contains the missing objects with their state set to absent.  

This plugin is helpful when Ansible runs from a pipeline and leverages a static configuration file that's tracked and maintained within a code repository.

## Install

- Place auto_absent.py in the lookup directory of your Ansible plugins path.
- Install the plugin requirements with PIP

> pip install -r requirements.txt

## Example

Old structure:

```
---
data:
- name: foo
  state: present
- name: bar
  state: present
```

New structure:

```
---
data:
- name: foo
  state: present
```

Playbook:

```
- name: Auto Absent
  set_fact: auto_absent="{{ lookup('auto_absent', old='old.yml', new='new.yml') }}"

- name: Config
  ansible.builtin.debug:
    msg: 
      - "{{ auto_absent }}"
```

auto_absent:

```
{
    "data": [
        {
            "name": "foo",
            "state": "present"
        },
        {
            "name": "bar",
            "state": "absent"
        }
    ]
}
```
