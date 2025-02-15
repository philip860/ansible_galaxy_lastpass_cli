# Ansible Collection - philip860.lastpass-cli

## LastPass CLI Ansible Collection

### Installation
To install the `philip860.lastpass_cli` Ansible collection, run the following command:

```sh
ansible-galaxy collection install philip860.lastpass_cli
```

### Usage
Below are sample playbooks demonstrating how to use the `lastpass_cli` module to retrieve and update a stored password.

#### Retrieve a Stored Password
```yaml
---
- name: Get LastPass info
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

#### Update a Stored Password
```yaml
---
- name: Update LastPass password
  hosts: localhost
  gather_facts: false
  become: yes
  tasks:
    - name: Update stored password
      philip860.lastpass_cli.lastpass_cli:
        username: "philipduncan860@gmail.com"
        password: password
        entry: "Passwords/Shared-ITS - IAM/Service-Accounts/automation-AAP"
        action: "update"
        new_password: "KD1906"
```

### Parameters
- `username`: The LastPass account username.
- `password`: The password for the LastPass account.
- `entry`: The path to the stored LastPass entry.
- `action`: The action to perform (`get` or `update`).
- `new_password`: The new password when using the `update` action.

### Example Execution
Run the playbook using:

```sh
ansible-playbook lastpass_playbook.yml
```

**Security Note:** Ensure you replace sensitive values with secure vault mechanisms or environment variables to enhance security.

