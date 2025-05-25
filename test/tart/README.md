# Test system using the Vagrant Tart Provider

## Recommendation: 4 CPUs and 8GB RAM

You can configure the number of CPUs and RAM in the `Vagrantfile`.

If the system is running while you change the configuration, restart it by

```shell
vagrant reload
```

## Running the test system

Launch the test system with

```shell
vagrant up
```

Once everything is installed, you can forward the RDP port to your host with

```shell
ssh -fN -i ../ssh_user_key/id_ecdsa -L 3389:localhost:3389 galadriel@$(tart ip lorien)
```

This will keep the SSH tunnel open in the background (`-fN`).

Connect to `localhost` with user `galadriel` and password `galadriel` using an
RDP client like Remmina, Windows App or Remote Desktop.

When you are done, disconnect the SSH tunnel with

```shell
ssh -O exit galadriel@$(tart ip lorien)
```

Then stop the test system with

```shell
vagrant halt
```

Note that the next boot will take about a minute, because the desktop
environment needs to be started.
