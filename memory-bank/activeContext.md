# Active Context: Ansible All My Things

## Current Work Focus

### Review Findings Resolution
**Primary Objective**: Fix identified issues in AWS implementation to make it production-ready:
- **Code Issues**: Resolve undefined variables and invalid AMI references
- **Configuration Simplification**: Streamline inventory and configuration files
- **Documentation Compliance**: Fix markdown violations and add missing sections
- **Integration Completion**: Merge MVP documentation into memory bank

**Status**: 6 of 12 findings completed, 6 remaining to fix sequentially with user review after each

**Approach**: Fix one finding per commit, request user review before proceeding to next finding

### MVP AWS Development Environment (Background Context)
**Objective**: Create secure, isolated AWS EC2 environments that provide:
- **Cross-Architecture Access**: Enable amd64 development from Apple Silicon (arm64) host systems
- **Secure Testing Environment**: Isolated environment for untrusted software (LLMs with MCP support)
- **Windows Foundation**: Linux implementation as stepping stone to Windows Server support
- **Cost Efficiency**: 10-15 minute provisioning with complete resource cleanup

**Long-term Vision**: Extend to Windows Server instances for Windows-specific development tools unavailable on macOS/Linux.

### Key Requirements for AWS MVP
- **Architecture**: amd64 (x86_64) to run tools unavailable on Apple Silicon
- **Instance Type**: t3.micro or t3.small (cost-effective, free tier eligible)
- **Operating System**: Ubuntu 24.04 LTS (current), Windows Server (future)
- **Storage**: 20GB GP3 EBS volume
- **Network**: Default VPC with SSH access from user's IP
- **Lifecycle**: Complete provision → configure → destroy cycle
- **Cost Target**: ~$8-10/month maximum (only when actively used)

## Recent Changes & Discoveries

### AWS Implementation Completed
- **AWS EC2 Provisioner**: Created `provisioners/aws-ec2.yml` with security group management
- **Dynamic Inventory**: Implemented `inventories/aws/aws_ec2.yml` for automatic host discovery
- **Simplified Configuration**: Minimal AWS-specific variables following Hetzner pattern
- **Complete Lifecycle**: Provision, configure, and destroy playbooks implemented
- **Cross-Architecture Documentation**: Updated use case and project brief for amd64 access

### Architecture Improvements Made
- **Configuration Minimalism**: Reduced AWS variables from 64 lines to essential 3 settings
- **Standardized Structure**: Updated provision.yml to match provision-aws.yml format
- **Core Architecture Drivers**: Established understandability, maintainability, extensibility
- **Quality Conflict Resolution**: Added guidance for handling competing design priorities
- **Provider Consistency**: Ensured identical patterns across Hetzner and AWS implementations

### Current Architecture Strengths
- **Provider Abstraction**: Clean separation between provisioning and configuration
- **Security Model**: Ansible Vault encryption, SSH key management, no hardcoded secrets
- **Testing Strategy**: Multi-provider testing ensures compatibility
- **Modular Design**: Individual playbooks for specific functionality
- **Configuration Simplicity**: Minimal provider-specific overrides for maintainability

## Next Steps

### Review Findings to Fix (Sequential Order)
1. 🔧 **Fix provisioners/aws-ec2.yml**: Resolve undefined `ansible_date_time` variable and invalid AMI ID
2. 🔧 **Simplify inventories/aws/aws_ec2.yml**: Reduce complexity following Hetzner pattern
3. 🔧 **Update playbooks/setup-desktop.yml**: Add required packages for AWS development environment
4. 🔧 **Fix docs/create-aws-vm.md**: Resolve markdown violations and add performance notes
5. 🔧 **Merge MVP Documentation**: Integrate implementation-plan.md and use-case-description.md
6. 🔧 **Cleanup MVP Directory**: Remove mvp-aws-dev-env/ after successful merge

### Completed Review Findings
1. ✅ **Memory Bank Updates**: Cross-architecture rationale documented
2. ✅ **Architecture Drivers**: Understandability, maintainability, extensibility established
3. ✅ **Quality Conflict Resolution**: Guidance for competing design priorities added
4. ✅ **Standardize provision.yml**: Structure updated to match provision-aws.yml
5. ✅ **Simplify vars.yml**: Reduced to minimal essential configuration parameters
6. ✅ **Clean docs/create-aws-vm.md**: Removed non-user-manual information

### Future Priorities (After Review Findings)
- **Test Integration**: Ensure existing playbooks work with AWS instances
- **Windows Planning**: Research Windows Server AMIs and configuration requirements

### Implementation Sequence
```mermaid
graph TD
    A[Create AWS Provisioner] --> B[Create AWS Inventory]
    B --> C[Define AWS Group Variables]
    C --> D[Test Basic Provisioning]
    D --> E[Test Full Configuration]
    E --> F[Test Destroy Process]
    F --> G[Document AWS Usage]
```

### Technical Decisions Needed
- **AWS Region**: Default to eu-north-1 or allow configuration?
- **Instance Naming**: Follow existing naming conventions
- **Security Groups**: Create dedicated or use default?
- **Key Pair Management**: Auto-generate or use existing?

## Active Patterns & Preferences

### Established Conventions
- **File Naming**: `setup-[functionality].yml` for configuration playbooks
- **Variable Naming**: `admin_user_on_fresh_system`, `ansible_user`, `my_desktop_user`
- **Directory Structure**: Provider-specific under `inventories/` and `provisioners/`
- **Testing Approach**: Local Vagrant testing before cloud deployment

### Code Quality Standards
- **Idempotency**: All tasks must be safely re-runnable
- **Error Handling**: Clear error messages for missing credentials
- **Documentation**: Inline comments for complex operations
- **Security**: No secrets in playbooks, all encrypted with Vault

### Integration Patterns
- **Dynamic Inventory**: Provider plugins for automatic host discovery
- **Group Variables**: Provider-specific configuration in `group_vars/`
- **Conditional Logic**: Provider-aware task execution
- **Symmetric Operations**: Backup/restore pairs for all configurations

## Important Learnings & Insights

### Multi-Provider Challenges
- **Admin Users**: Each provider has different initial admin user (root, admin, vagrant)
- **Desktop Support**: Docker containers cannot run desktop environments
- **Network Configuration**: Provider-specific networking requirements
- **Cost Management**: Critical to have reliable destroy operations

### Ansible Best Practices Discovered
- **Early User Creation**: Switch from admin to ansible user immediately
- **SSH Key Management**: Automated key pair creation and distribution
- **Vault Integration**: Seamless encryption without manual password entry
- **Testing Strategy**: Multiple provider testing catches edge cases

### Security Considerations
- **Credential Isolation**: Environment variables for provider authentication
- **Access Control**: Minimal privilege escalation, sudo only when needed
- **Network Security**: SSH-only access, no password authentication
- **Data Protection**: All sensitive data encrypted at rest

## Current Challenges

### AWS Integration Unknowns
- **Collection Requirements**: Need to verify `amazon.aws` collection compatibility
- **Authentication Flow**: AWS credentials vs. Hetzner token approach
- **Instance Discovery**: Dynamic inventory configuration for EC2
- **Cost Monitoring**: Ensuring complete resource cleanup

### Testing Considerations
- **AWS Costs**: Need to minimize testing costs during development
- **Credential Management**: Secure handling of AWS credentials in testing
- **Provider Parity**: Ensuring AWS behaves identically to Hetzner
- **Documentation**: Clear setup instructions for AWS credentials

## Context for Future Work

### Extension Opportunities
- **Windows Server Support**: AWS EC2 Windows instances for Windows-specific development
- **Additional Providers**: Google Cloud, DigitalOcean, Azure
- **Enhanced Security**: Advanced hardening, monitoring, logging
- **Application Support**: Additional development tools and applications
- **Automation**: CI/CD integration, scheduled operations

### Maintenance Considerations
- **Provider API Changes**: Monitor for breaking changes in cloud APIs
- **Ubuntu Updates**: Track LTS releases and migration paths
- **Ansible Evolution**: Stay current with Ansible and collection updates
- **Security Updates**: Regular review of security practices

### User Experience Goals
- **Cross-Architecture Transparency**: Seamless amd64 access from Apple Silicon host
- **Platform Flexibility**: Easy switching between Linux and Windows environments
- **Simplicity**: Single command provisioning across all providers
- **Reliability**: Consistent behavior regardless of provider choice
- **Transparency**: Clear feedback on operations and costs
- **Cost Awareness**: Clear understanding of architectural benefits vs. costs

## Memory Bank Maintenance Notes
- **Last Updated**: Initial creation during memory bank initialization
- **Next Review**: After AWS MVP implementation completion
- **Key Files to Monitor**: AWS provisioner, inventory, and group variables
- **Success Metrics**: 10-15 minute provision time, zero ongoing costs, identical UX to Hetzner
