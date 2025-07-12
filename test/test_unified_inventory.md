# Test unified inventory

The following test verifies that the unified inventory shows all instances across the cloud providers:

```
GIVEN hobbiton is a Linux instance hosted in the Hetzner Cloud
AND rivendell is a Linux instance hosted in the AWS EC2 cloud
AND moria is a Windows instance hosted in the AWS EC2 cloud

WHEN I execute the command `ansible-inventory --graph`

THEN I see the output

@all:
  |--@ungrouped:
  |--@aws_ec2:
  |  |--moria
  |  |--rivendell
  |--@aws_ec2_linux:
  |  |--rivendell
  |--@aws_ec2_windows:
  |  |--moria
  |--@hcloud_linux:
  |  |--hobbiton
  |--@windows:
  |  |--moria
  |--@linux:
  |  |--rivendell
  |  |--hobbiton
  |--@hcloud:
  |  |--hobbiton
```

## Manual test instructions

```shell
# Environment setup
export AWS_ACCESS_KEY_ID="your-aws-key"
export AWS_SECRET_ACCESS_KEY="your-aws-secret"
export AWS_DEFAULT_REGION="eu-north-1"
echo -n "hcloud API token: "; read -s HCLOUD_TOKEN; export HCLOUD_TOKEN
export ANSIBLE_VAULT_PASSWORD_FILE="./ansible-vault-password.txt"
export ANSIBLE_HOST_KEY_CHECKING=False

# Assert: No instances are running
ansible-inventory --graph

# GIVEN hobbiton is a Linux instance hosted in the Hetzner Cloud
ansible-playbook provision.yml --vault-password-file ansible-vault-password.txt

# AND rivendell is a Linux instance hosted in the AWS EC2 cloud
ansible-playbook provision-aws-linux.yml --vault-password-file ansible-vault-password.txt

# AND moria is a Windows instance hosted in the AWS EC2 cloud
ansible-playbook provision-aws-windows.yml --vault-password-file ansible-vault-password.txt

# WHEN I execute the command `ansible-inventory --graph`
ansible-inventory --graph

# THEN I see the output ... (requires manual verification)

# Test destroying all instances
ansible-playbook destroy.yml
ansible-playbook destroy-aws.yml

# Assert: No instances are running
ansible-inventory --graph
```