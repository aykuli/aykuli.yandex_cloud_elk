#!/usr/bin/python

# @src https://docs-ansible-com.translate.goog/projects/ansible/latest/dev_guide/developing_modules_general.html?_x_tr_sl=en&_x_tr_tl=ru&_x_tr_hl=ru&_x_tr_pto=sge#id3

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import os

DOCUMENTATION = r'''
---
module: fcreate

short_description: Module to create a file with provided content

version_added: "1.0.0"

description: Module to create a file with provided content by the path.

options:
    path:
        description: The path where the file should be created.
        required: true
        type: str
    content:
        description: The content to write to the file. If the file already exists, it checks if content hash is different, it will be overwritten.
        required: false
        type: str

author:
    - Aynur Shauerman (@aykuli)
'''

EXAMPLES = r'''
# Pass in a message
- name: Create a file with content
  aykuli.yandex_cloud_elk.fcreate:
    path: /tmp/test.txt
    content: hello world

# Create a file with content and have changed true
- name: Create a file with content and changed output
  aykuli.yandex_cloud_elk.fcreate:
    path: /tmp/test.txt
    content: another hello world

# Create empty file
- name: Create empty file
  aykuli.yandex_cloud_elk.fcreate:
    path: /tmp/test.txt

# fail the module
- name: Test failure of the module
  aykuli.yandex_cloud_elk.fcreate:
    path: /tmp/test.txt
    content: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: file stats
'''

import os
from ansible.module_utils.basic import AnsibleModule

# todo logic of creating folders split path and so on


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
      path=dict(type='str', required=True, default="inventory/prod.yml"),
      content=dict(type='str', required=False)
    )
    module = AnsibleModule(
      argument_spec      =module_args,
      supports_check_mode=True
    )
    path    = module.params['path']
    content = module.params['content'] if module_args['content'] else ''

    # 1 Init the default response structure
    result = dict(changed=True, message=path)

    # 2 Implement Idempotency (Check current state)
    is_file_exists = os.path.exists(path)
    curr_content = ''

    if is_file_exists:
      with open(path, 'r') as f:
        curr_content = f.read()
    if not is_file_exists or curr_content != content:
      result['changed'] = True

    # 3. Handle Check Mode
    if module.check_mode:
        module.exit_json(**result)

    if module.params['content'] == 'fail me':
      module.fail_json(msg='You requested this to fail', **result)

    # 4. Perform the Remote Action (Only if changes are needed)
    if result['changed']:
      try:
        with open(path, 'w') as f:
          f.write(content)
          result["message"] = os.stat(path)
      except Exception as e:
        module.fail_json(msg = f"Failed to write file: {str(e)}", **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
