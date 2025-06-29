# Obtain Remote IP Address

Depending on the provider, the IP address of the remote server can be
queried using one of the following commands:

```shell
# Hetzner Cloud
export IPV4_ADDRESS=$(hcloud server list -o json | jq '.[0].public_net.ipv4.ip' | tr -d '"'); echo "IPv4 address: \"$IPV4_ADDRESS\""

# AWS
# The Linux VM name is lorien,
export AWS_INSTANCE=lorien

# the Windows VM name is lorien-windows
export AWS_INSTANCE=lorien-windows

export IPV4_ADDRESS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$AWS_INSTANCE" "Name=instance-state-name,Values=running" --query 'Reservations[*].Instances[*].PublicIpAddress' --output text)

echo "IP of AWS instance $AWS_INSTANCE: $IPV4_ADDRESS"

# Tart provider for Vagrant
export IPV4_ADDRESS=$(tart ip lorien); echo "IPv4 address: \"$IPV4_ADDRESS\""

# Docker provider for Vagrant
export IPV4_ADDRESS=127.0.0.1
```
