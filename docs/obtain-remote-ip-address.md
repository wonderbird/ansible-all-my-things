# Obtain Remote IP Address

## General Ansible Inventory Lookup

You can query the ansible inventory for the host ip address:

```shell
export HOSTNAME=lorien; \
export IPV4_ADDRESS=$(ansible-inventory --list | jq --raw-output "._meta.hostvars.$HOSTNAME.ansible_host"); \
echo $IPV4_ADDRESS
```

The remaining sections show provider specific instructions.

## Hetzner Cloud

```shell
# Assuming there is only one instance:
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""
```

## AWS

```shell
# The Linux VM name is rivendell,
export AWS_INSTANCE=rivendell

# the Windows VM name is moria
export AWS_INSTANCE=moria

# Get IP address of an AWS instance
export IPV4_ADDRESS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$AWS_INSTANCE" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text); echo "IP of AWS instance $AWS_INSTANCE: $IPV4_ADDRESS"
```

## Tart

```shell
# Get IP address for Tart Vagrant provider
export IPV4_ADDRESS=$(tart ip lorien); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Get IP address for Docker Vagrant provider
export IPV4_ADDRESS=127.0.0.1
```
