# Test system using the Vagrant Tart Provider

## Recommendation: 4 CPUs and 8GB RAM

You can configure the number of CPUs and RAM in the `Vagrantfile`.

If the system is running while you change the configuration, restart it by

```shell
vagrant reload
```

## Provisioning the Test System

Provision the system

```shell
vagrant up
```

> [!IMPORTANT] Get the IP address from tart
>
> If you use `./configure.sh lorien` you will get the wrong IP, because the
> static inventory contains the old address.

```shell
tart ip lorien
```

Update the IP address in the inventory file [/inventories/vagrant_tart.yml](../../inventories/vagrant_tart.yml)

Install packages for this particular system type

```shell
ansible-playbook ./configure-linux.yml --skip-tags "not-supported-on-vagrant-arm64"
```
