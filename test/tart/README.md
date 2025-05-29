# Test system using the Vagrant Tart Provider

## Recommendation: 4 CPUs and 8GB RAM

You can configure the number of CPUs and RAM in the `Vagrantfile`.

If the system is running while you change the configuration, restart it by

```shell
vagrant reload
```

## Run the test system

The following instructions show how to run a test system with Vagrant.
For the Docker provider, executed the same commands from the `test/docker`
folder.

```shell
cd test/tart

# Initialize the local test system
vagrant up

# Verify the configuration
# The following command should show that ansible uses the user configured
# in Vagrantfile (extra_vars) and the host name is "lorien"
ansible dev -m shell -a "whoami"

# List the users we have added to the system
ansible dev -m shell -a 'ls /home'

# Stop the local test system
vagrant halt

# Restart the local test system
# Note that booting will take about a minute, because the desktop environment
# needs to be loaded.
vagrant up

# Destroy the local test system
vagrant destroy -f
```

## Log in as the desktop user

Refer to [Work with a VM](../../docs/work-with-vm.md) for instructions on how to
log in as the desktop user.
