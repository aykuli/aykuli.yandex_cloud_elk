# aykuli.yandex_cloud_elk Ansible Collection

Content
-------

- [Description](#description)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage Example](#usage-example)
- [Modules Docs](#modules-docs)

Description
----------

The Ansible aykuli.yandex_cloud_elk collection of version 1.0.0 includes:
* module to create Virtual Machines in Yandex Cloud as many as you privide in params of `aykuli.yandex_cloud_elk.vms` module.

Requirements
------------

* `yc` cli configured for your YC account
* `ansible-core` >= 2.20
* `Python` 3.9 or greater.

Installation
------------

```bash
ansible-galaxy collection install aykuli.yandex_cloud_elk
```

Usage Example
-------

* Example 1: Creating Vms with default parameters

[Simple playbook example here](./playbooks/play.yml):

```yaml
---
- name: Сreate VMs and inventory file for them
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create Yandex Cloud VMs
      aykuli.yandex_cloud_elk.vms:
        image_family: 'ubuntu-2404-lts'
        names:
          - clickhouse
          - vector
          - lighthouse
      register: result_vms
    - name: Print resulting messages of creating VMs
      ansible.builtin.debug:
        msg: "{{ result_vms }}"
    - name: Write prev content to inventory/prod.yml file
      aykuli.yandex_cloud_elk.fcreate:
        path: inventory/prod.yml
        content: "{{ result_vms.message }}"
```

* Example 2: Creating Vms with custom parameters:

```yaml
- name: Сreate VMs and inventory file for them
  hosts: localhost
  gather_facts: false
  tasks:
    - name: Create Yandex Cloud VMs with custom parameters
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
      register: result_vms
    - name: Print resulting messages of creating VMs
      ansible.builtin.debug:
        msg: "{{ result_vms }}"
    - name: Write prev content to inventory/prod.yml file
      aykuli.yandex_cloud_elk.fcreate:
        path: inventory/prod.yml
        content: "{{ result_vms.message }}"
```



As a result there will be created `inventory/prod.yml` file with similar content:

```yaml
clickhouse:
  hosts:
    clickhouse:
      ansible_host: XXX.XXX.XXX.XXX
      ansible_user: ubuntu
      ansible_become: true

lighthouse:
  hosts:
    lighthouse:
      ansible_host: XXX.XXX.XXX.XXX
      ansible_user: ubuntu
      ansible_become: true

vector:
  hosts:
    vector:
      ansible_host: XXX.XXX.XXX.XXX
      ansible_user: ubuntu
      ansible_become: true


```

In the console you should see something like that:

```bash
$ ansible-playbook play.yml 
PLAY [Сreate VMs and inventory file for them] ********************************************

TASK [Create Yandex Cloud VMs] ***********************************************************
changed: [localhost]

TASK [Print resulting messages of creating VMs] ******************************************
ok: [localhost] => {
    "msg": {
        "changed": true,
        "failed": false,
        "message": "clickhouse:\n  hosts:\n    clickhouse:\n      ansible_host: XXX.XXX.XXX.XXX\n      ansible_user: ubuntu\n      ansible_become: true\n\nlighthouse:\n  hosts:\n    lighthouse:\n      ansible_host: XXX.XXX.XXX.XXX\n      ansible_user: ubuntu\n      ansible_become: true\n\nvector:\n  hosts:\n    vector:\n      ansible_host: XXX.XXX.XXX.XXX\n      ansible_user: ubuntu\n      ansible_become: true\n\n"
    }
}

TASK [Write prev content to inventory/prod.yml file] *************************************
changed: [localhost]

PLAY RECAP *******************************************************************************
localhost                  : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```

Modules Docs
------------

<details>
<summary>aykuli.yandex_cloud_elk.vms</summary>

```yaml
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
```
</details>

<details>
<summary>aykuli.yandex_cloud_elk.fcreate</summary>

```yaml
module: fcreate

short_description: Module to create a file with provided content

version_added: "1.0.0"

description: Module to create a file with provided content by the path.

options:
    path:
        description: The path where the file should be created.
        default: inventory/prod.yml
        required: true
        type: str
    content:
        description: The content to write to the file. If the file already exists, it checks if content hash is different, it will be overwritten.
        required: false
        type: str

author:
    - Aynur Shauerman (@aykuli)
```
</details>

