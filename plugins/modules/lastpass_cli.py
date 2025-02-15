#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import subprocess
import os
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = r'''
---
module: lastpass_cli

short_description: Ansible module for managing credentials with lastpass-cli

version_added: "1.0.0"

description:
    - This module allows users to log into LastPass, retrieve stored credentials, and update passwords using the lastpass-cli tool.

options:
    username:
        description: The LastPass account username for authentication.
        required: true
        type: str
    password:
        description: The LastPass master password for authentication.
        required: true
        type: str
    entry:
        description: The LastPass entry name to retrieve or update.
        required: true
        type: str
    action:
        description: The action to perform ("get" to retrieve, "update" to change password).
        required: true
        choices: ["get", "update"]
        type: str
    new_password:
        description: The new password when updating an entry.
        required: false
        type: str

author:
    - Your Name (@yourGitHubHandle)
'''

EXAMPLES = r'''
# Retrieve password from LastPass
- name: Get stored password
  lastpass_cli:
    username: "philipduncan860@gmail.com"
    password: "mysecurepassword"
    entry: "Passwords/Shared-ITS - IAM/Service-Accounts/demo-netid-automation"
    action: "get"

# Update password in LastPass
- name: Update stored password
  lastpass_cli:
    username: "philipduncan860@gmail.com"
    password: "mysecurepassword"
    entry: "Passwords/Shared-ITS - IAM/Service-Accounts/demo-netid-automation"
    action: "update"
    new_password: "newsecurepassword"
'''

RETURN = r'''
original_message:
    description: The original parameters passed to the module.
    type: dict
    returned: always
message:
    description: The output message of the module.
    type: str
    returned: always
password:
    description: The retrieved password (only for 'get' action).
    type: str
    returned: when action is 'get'
'''

def run_module():
    module_args = dict(
        username=dict(type='str', required=True, no_log=True),
        password=dict(type='str', required=True, no_log=True),
        entry=dict(type='str', required=True),
        action=dict(type='str', required=True, choices=['get', 'update']),
        new_password=dict(type='str', required=False, no_log=True)
    )

    result = dict(
        changed=False,
        original_message='Input parameters received',
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        module.exit_json(**result)

    username = module.params['username']
    password = module.params['password']
    entry = module.params['entry']
    action = module.params['action']
    new_password = module.params.get('new_password', None)

    try:
        # Ensure required directories exist
        lpass_dir = os.path.expanduser("~/.local/share/lpass")
        root_lpass_dir = "/root/.local/share/lpass"
        if not os.path.exists(lpass_dir):
            os.makedirs(lpass_dir, exist_ok=True)
        if os.geteuid() == 0 and not os.path.exists(root_lpass_dir):
            os.makedirs(root_lpass_dir, exist_ok=True)

        # Ensure LastPass session exists
        session_status_cmd = "lpass status"
        session_status = subprocess.run(session_status_cmd, shell=True, capture_output=True, text=True)

        if "Not logged in" in session_status.stdout:
            try:
                # Log in using piped password
                login_cmd = f"echo '{password}' | LPASS_DISABLE_PINENTRY=1 lpass login {username}"
                login_result = subprocess.run(login_cmd, shell=True, capture_output=True, text=True)

                if login_result.returncode != 0:
                    result['message'] = f"Login failed. Ensure '/root/.local/share/lpass' exists. Run: mkdir -p /root/.local/share/lpass"
                    module.exit_json(**result)
            except Exception as e:
                result['message'] = str(e)
                module.exit_json(**result)

        # Perform requested action
        if action == 'get':
            get_cmd = f"lpass show --password '{entry}'"
            get_result = subprocess.run(get_cmd, shell=True, capture_output=True, text=True)

            if get_result.returncode != 0:
                result['message'] = f"Failed to retrieve password: {get_result.stderr.strip()}"
                module.exit_json(**result)

            retrieved_password = get_result.stdout.strip()
            result['password'] = retrieved_password
            result['message'] = "Password retrieved successfully."

        elif action == 'update':
            if not new_password:
                result['message'] = "New password must be provided for update action."
                module.exit_json(**result)

            update_cmd = f"echo '{new_password}' | LPASS_DISABLE_PINENTRY=1 lpass edit \"{entry}\" --password --non-interactive"
            update_result = subprocess.run(update_cmd, shell=True, capture_output=True, text=True)

            if update_result.returncode != 0:
                result['message'] = f"Failed to update password: {update_result.stderr.strip()}"
                module.exit_json(**result)

            result['changed'] = True
            result['message'] = "Password updated successfully."

        # Logout from LastPass to clean up session
        logout_cmd = "lpass logout --force"
        subprocess.run(logout_cmd, shell=True, capture_output=True, text=True)

        module.exit_json(**result)

    except Exception as e:
        result['message'] = str(e)
        module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
