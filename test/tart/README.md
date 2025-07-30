# Test system using the Vagrant Tart Provider

## Recommendation: 4 CPUs and 8GB RAM

You can configure the number of CPUs and RAM in the `Vagrantfile`.

If the system is running while you change the configuration, restart it by

```shell
vagrant reload
```

## Provisioning the Test System

```shell
# Provision the system
vagrant up

# Update the IP address in the inventory file /inventories/vagrant_tart.yml
# Query the IP address as follows:
tart ip lorien

# Install packages for this particular system type
ansible-playbook configure-linux.yml --skip-tags "not-supported-on-vagrant-arm64" --vault-password-file ansible-vault-password.txt
```
