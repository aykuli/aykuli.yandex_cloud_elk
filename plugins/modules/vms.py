#!/usr/bin/python

# Copyright: (c) 2026, Aynur Shauerman <aykuli@ya.ru>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import subprocess
import json
import os


DOCUMENTATION = r'''
---
module: vms

short_description: Creating Yandex Cloud Virtual Machines

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Creating Yandex Cloud Virtual Machines

options:
    image_family:
        description: OS image family from Yandex Cloud standard image library
        required: false
        type: str
    names:
        description: List of VMs hostnames
        required: false
        type: list(str)
    network_name:
        description: Network name where all VMs will be placed in
        required: false
        type: str
    subnet_name:
        description: Network's subnet name where all VMs will be placed in
        required: false
        type: str
    zone:
        description: Specify zone in Yandex Cloud availability zones
        required: false
        type: str
    platform:
        description: это идентификатор аппаратной платформы виртуальной машины в контексте сервиса Yandex Compute Cloud. 
        required: false
        type: str
    ip_range:
        description: диапазон IP-адресов в облачной сети, адреса из которого могут назначаться виртуальным машинам 
        required: false
        type: str
    preemptible:
        description: Указыываем прерываемая ВМ или нет
        required: false
        type: str
    cores:
        description: Количество ядер ЦПУ ВМ
        required: false
        type: str
    memory:
        description: Размер ОЗУ отдельной ВМ
        required: false
        type: str
    core_fraction:
        description: Процент захвата ЦПУ виртуальной машиной на машине гипервизора видимо
        required: false
        type: str
    disk_size:
        description: Размер жёсктого диска отдельной ВМ
        required: false
        type: str
    user:
        description: Имя пользователя на ВМ
        required: false
        type: str
    ssh_key:
        description: Путь к публичному ключу shh. если его не задать, то к ВМ по shh будет не зайти.
        required: false
        type: str

extends_documentation_fragment:
    - aykuli.yandex_cloud_elk.vms

author:
    - Aynur Shauerman (@aykuli)
'''

EXAMPLES = r'''
- name: Создание ВМ по настройкам по умолчанию
 aykuli.yandex_cloud_elk.vms:

- name: Создание ВМ по кастомным настройкам
  aykuli.yandex_cloud_elk.vms:
    names:
      - clickhouse
      - vector
      - lighthouse
    image_family: centos-7
    network_name: my-network
    subnet_name: my-sub-network
    zone: ru-central1-d
    platform: standard-v3
    ip_range: 192.168.10.0/24
    preemptible: False
    cores: "2"
    memory: 8GB
    core_fraction: 100
    disk_size: 20GB
    user : buddy
    ssh_key: /home/buddy/.shh/id_rsa.pub
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        image_family = dict(type='str',  default="ubuntu-2404-lts"),
        names        = dict(type="list", default=["vector","clickhouse",'lighthouse']),
        network_name = dict(type="str",  default="ayn-net"),
        subnet_name  = dict(type="str",  default="ayn-subnet"),
        zone         = dict(type="str",  default="ru-central1-a"),
        platform     = dict(type="str",  default="standard-v2"),
        ip_range     = dict(type="str",  default="192.168.10.0/2"),
        preemptible  = dict(type="bool", default=True),
        cores        = dict(type="str",  default="2"),
        memory       = dict(type="str",  default="2GB"),
        core_fraction = dict(type="str",  default="5"),
        disk_size    = dict(type="str",  default="10GB"),
        user         = dict(type="str", default="ubuntu"),
        ssh_key      = dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    
    instances_json = create_vpc_and_vms(params = module.params)
    message = create_inventory_content(instances_json, module.params["user"])

    result = dict(
        changed=True,
        message=message
    )

    if module.check_mode:
        module.exit_json(**result)

    module.exit_json(**result)

def create_vpc_and_vms(params):
  net_id = None
  net = subprocess.run([
    "yc", "vpc", "network", "create",
    "--name", params["network_name"],
    "--format", "json"
  ], capture_output=True)
  if net.returncode == 0:
   net_data = json.loads(net.stdout)
   net_id = net_data["id"]
  else:
    net_info = subprocess.getoutput(f"yc vpc net get {params["network_name"]} --format json")
    net_data = json.loads(net_info)
    net_id = net_data["id"]

  subnet=subprocess.run([
    "yc", "vpc", "subnet", "create",
    "--name", params["subnet_name"],
    "--network-id", net_id,
    "--range", params["ip_range"],
    "--zone", params["zone"]
  ], capture_output=True)
  if subnet.returncode == 0:
    subnet_data = json.loads(subnet.stdout)
    subnet_id = subnet_data["id"]
  else:
    subnet_info = subprocess.getoutput(f"yc vpc subnet get {params["subnet_name"]} --format json")
    subnet_data = json.loads(subnet_info)
    subnet_id = subnet_data["id"]

  instances = []

  ssh_file = params["ssh_key"]
  is_file_exists = os.path.exists(ssh_file)
  ssh_pub_key = ''

  if is_file_exists:
    with open(ssh_file, 'r') as f:
      ssh_pub_key = f.read()


  for name in params["names"]:
    vm = subprocess.run([
      "yc", "compute", "instance", "create",
      "--name", name,
      "--platform", params["platform"],
      "--zone", params["zone"],
      "--cores", params["cores"],
      "--memory", params["memory"],
      "--preemptible", params["preemptible"],
      "--core-fraction", params["core_fraction"],
      "--network-interface", f"subnet-id={subnet_id},nat-ip-version=ipv4",
      "--create-boot-disk", f"image-family={params["image_family"]},image-folder-id=standard-images,size={params["disk_size"]}",
      "--metadata", f"ssh-keys={params["user"]}:{ssh_pub_key}",
      "--format", "json"
    ], capture_output=True)
    if vm.returncode == 0:
      vm_data = json.loads(vm.stdout)
      instances.append({
        "name": vm_data["name"],
        "ip": vm_data["network_interfaces"][0]["primary_v4_address"]["one_to_one_nat"]["address"],
      })
  return instances

def create_inventory_content(vms_dict, username = "ubuntu"):
  lines = []
  for vm in vms_dict:
    lines.append(f"""{vm["name"]}:
  hosts:
    {vm["name"]}:
      ansible_host: {vm["ip"]}
      ansible_user: {username}
      ansible_become: true
""")
  return "\n".join(lines) + "\n"

if __name__ == '__main__':
    run_module()