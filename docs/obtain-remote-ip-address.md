# Obtain Remote IP Address

Depending on the provider, the IP address of the remote server can be
queried using one of the following commands:

```shell
# Hetzner Cloud
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Tart provider for Vagrant
export IPV4_ADDRESS=$(tart ip lorien); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Docker provider for Vagrant
export IPV4_ADDRESS=127.0.0.1
```
