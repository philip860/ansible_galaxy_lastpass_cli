# Ansible Collection - philip860.lastpass-cli

# LastPass CLI Ansible Collection

## Installation
To install the `philip860.lastpass_cli` Ansible collection, run the following command:

```sh
ansible-galaxy collection install philip860.lastpass_cli
```

## Usage
Below is a sample playbook demonstrating how to use the `lastpass_cli` module to retrieve a stored password:

```yaml
---
- name: Get lastpass info
  hosts: localhost
  gather_facts: false
  become: yes
  tasks:
    - name: Get stored password
      philip860.lastpass_cli.lastpass_cli:
        username: "philipduncan860@gmail.com"
        password: password
        entry: "Passwords/Shared-ITS - IAM/Service-Accounts/automation-AAP"
        action: "get"
```

## Parameters
- `username`: The LastPass account username.
- `password`: The password for the LastPass account.
- `entry`: The path to the stored LastPass entry.
- `action`: The action to perform (e.g., `get`).

## Example Execution
Run the playbook using:

```sh
ansible-playbook lastpass_playbook.yml
```

Ensure you replace sensitive values with secure vault mechanisms or environment variables for better security.

