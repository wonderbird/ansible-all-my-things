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

This takes 10 - 20 seconds.

> [!IMPORTANT] Refresh IP address from tart
>
> If you use `./configure.sh lorien` you will get the wrong IP, because the
> static inventory contains the old address.

```shell
export IPV4_ADDRESS=$(tart ip lorien); echo $IPV4_ADDRESS
```

Update the IP address in the inventory file [/inventories/vagrant_tart.yml](../../inventories/vagrant_tart.yml)

Configure the environment variables needed for the ansible scripts:

```shell
cd ../..; . ./configure.sh lorien; cd test/tart
```

Install packages for this particular system type

```shell
cd ../..; ansible-playbook ./configure-linux.yml --skip-tags "not-supported-on-vagrant-arm64"; cd test/tart
```

## Troubleshooting: Changed Remote Host Identification

If you receive an error message warning you about a changed remote host identification AND if you recently deleted a tart VM with the same ip address, then remove the SSH key from `~/.ssh/known_hosts`

```shell
ssh-keygen -R $IPV4_ADDRESS
```

and login once manually in order to accept the new host key

```shell
ssh admin@$IPV4_ADDRESS
```

You don't need to complete the login by entering the password. Instead you can hit CTRL+C.

After that you can run the `configure-linux.yml` playbook again.
