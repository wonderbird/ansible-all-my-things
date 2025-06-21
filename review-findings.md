- [ ] provision-aws.yml is not idempotent. When called twice, it creates another instance instead of keeping the number of created instances at 1.

- [ ] `ansible-inventory -i inventories/aws/aws_ec2.yml --graph` does not show the provisioned instances. The graph shows

```
@all:
  |--@ungrouped:
  |--@aws_ec2:
```
