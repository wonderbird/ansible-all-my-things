# Use Cases

This repository provides Infrastructure-as-Code automation for cross-platform development environments with built-in AI agent safety controls. Infrastructure-as-Code means using code to automatically provision, configure, and manage computing resources instead of manual setup.

## Primary Scenarios

### Cross-Platform Development

**The Problem**: You need access to different operating systems and applications for development, but don't want to maintain multiple physical machines or complex dual-boot setups.

**The Solution**: Automatically provision Linux and Windows development environments on cloud providers (AWS, Hetzner Cloud) that you can access remotely via SSH or remote desktop. These environments come pre-configured with development tools and can be created or destroyed on-demand.

**When to Use**: You develop applications that need to work on multiple platforms, or you need access to platform-specific applications (like Windows-only software) from a different host operating system.

### AI Agent Safety on Development Systems  

**The Problem**: AI coding assistants (such as Claude Code, GitHub Copilot, Cursor, or similar tools) can accidentally execute dangerous infrastructure commands when working on automation projects. Commands like `ansible-playbook destroy.yml` or `docker system prune -a` could destroy the very systems the AI is trying to help with.

**The Solution**: Deploy command restrictions to development systems that block AI agents from running infrastructure commands while preserving normal development capabilities. The restrictions are applied only to specific user accounts where AI agents operate, leaving human users unaffected.

**When to Use**: You use AI coding assistants for infrastructure automation work and need to prevent accidental system damage while maintaining AI productivity for normal development tasks.

### Cost-Optimized Infrastructure

**The Problem**: Different development workflows have different resource requirements and cost profiles. You want to choose the most cost-effective infrastructure for each specific need.

**The Solution**: Multiple deployment options across different cloud providers, each optimized for different usage patterns:
- Persistent development environments for ongoing work
- On-demand environments for temporary tasks
- Windows servers for platform-specific application access

**When to Use**: You want to optimize infrastructure costs by matching resource allocation to actual usage patterns rather than maintaining over-provisioned static environments.

## Development Environment Options

When working with this system, you can choose from three development approaches:

### Docker-Based Testing (Fast & Limited)
**When to Choose**: Quick validation of automation scripts, syntax checking, or basic functionality testing.
- **Pros**: Starts in seconds, lightweight resource usage, works anywhere Docker runs
- **Cons**: Cannot validate AI agent safety features, limited to basic automation testing
- **Best for**: Initial development, script debugging, contribution testing

### VM-Based Testing (Complete & Local)
**When to Choose**: Full feature validation including AI agent safety, offline development (except AI API calls), or comprehensive testing without cloud costs.
- **Pros**: Complete feature validation, no cloud infrastructure costs, production-similar environment
- **Cons**: Higher resource usage, longer startup time, requires VM-capable hardware
- **Best for**: Feature development, AI safety validation, cost-conscious development

### Cloud-Based Testing (Production-Identical)
**When to Choose**: Final validation, production environment testing, or when local resources are insufficient.
- **Pros**: Identical to production deployment, full platform diversity, no local resource constraints
- **Cons**: Infrastructure costs, internet dependency, longer provisioning time
- **Best for**: Production preparation, final testing, team environments

## AI Agent Safety Note

If you use AI coding assistants, the command restriction features require VM-based or cloud-based environments. Container-based testing cannot validate these safety features due to kernel security limitations. See [test/docker/README.md](../test/docker/README.md#limitations) for details.