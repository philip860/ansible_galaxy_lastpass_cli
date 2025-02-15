#!/usr/bin/python

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import subprocess
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

def ensure_directory(directory):
    """Ensures the directory exists, is writable, and has correct permissions."""
    if not os.path.exists(directory):
        try:
            subprocess.run(["mkdir", "-p", directory], check=True)
            subprocess.run(["chmod", "700", directory], check=True)
        except subprocess.CalledProcessError as e:
            return f"Failed to create directory {directory}: {str(e)}"
    return None

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
        original_message='',
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

    # Detect if running as root or inside /root directory
    if os.geteuid() == 0 or os.getcwd().startswith("/root"):
        home_directory = "/root/.local/share"
    else:
        home_directory = os.path.expanduser("~/.local/share")

    # Ensure directory exists
    error = ensure_directory(home_directory)
    if error:
        module.fail_json(msg=error, **result)

    # Set LastPass home environment variable
    os.environ["LPASS_HOME"] = home_directory

    # Ensure LastPass session exists
    session_status_cmd = "lpass status"
    session_status = subprocess.run(session_status_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    if "Not logged in" in session_status.stdout:
        # Log in using piped password
        login_cmd = f"echo '{password}' | LPASS_DISABLE_PINENTRY=1 lpass login {username}"
        login_result = subprocess.run(login_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if login_result.returncode != 0:
            module.fail_json(msg=f"Failed to log in to LastPass: {login_result.stderr.strip()}", **result)

    # Perform requested action
    if action == 'get':
        # Retrieve password from LastPass
        get_cmd = f"lpass show --password '{entry}'"
        get_result = subprocess.run(get_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if get_result.returncode != 0:
            module.fail_json(msg=f"Failed to retrieve password: {get_result.stderr.strip()}", **result)

        retrieved_password = get_result.stdout.strip()
        result['password'] = retrieved_password
        result['message'] = "Password retrieved successfully."

    elif action == 'update':
        if not new_password:
            module.fail_json(msg="New password must be provided for update action.", **result)

        # Update password securely
        update_cmd = f"echo '{new_password}' | lpass edit '{entry}' --password --non-interactive"
        update_result = subprocess.run(update_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        if update_result.returncode != 0:
            module.fail_json(msg=f"Failed to update password: {update_result.stderr.strip()}", **result)

        result['changed'] = True
        result['message'] = "Password updated successfully."

    # Logout from LastPass to clean up session
    logout_cmd = "lpass logout --force"
    subprocess.run(logout_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
