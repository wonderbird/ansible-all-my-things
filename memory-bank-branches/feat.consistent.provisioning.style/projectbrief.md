# Project Brief: Ansible All My Things

## Project Overview
An Ansible-based infrastructure automation system for personal IT environment management, enabling cross-platform development environments with comprehensive testing infrastructure.

## Core Purpose
Automate complete lifecycle of development environments across cloud providers with comprehensive testing, with emphasis on:
- **Cross-Platform Access**: Enable platform-specific applications from any host system
- **Multi-Provider Support**: AWS, Hetzner Cloud, and Vagrant environments
- **Cost Efficiency**: On-demand provisioning with complete resource cleanup
- **Testing Infrastructure**: Comprehensive testing framework with Vagrant providers
- **Unified Interface**: Consistent command patterns across all environments

## Key Requirements

### Current Development Track: Unified Vagrant Docker Provisioning

#### Track 1: CURRENT MVP 🎯 IN PROGRESS (2-3 days)
- **Target Goal**: Unified provisioning command for Vagrant Docker environment (dagorlad) ⏳ ACTIVE
- **Business Driver**: Urgent need for consistent provisioning commands across cloud VMs and Vagrant VMs ⏳ PRIORITY
- **Command Pattern**: `ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux"` ⏳ TARGET
- **Foundation**: Built on existing provider/platform parameter system and mature testing infrastructure ⏳ READY
- **Timeline**: 2-3 days with test-first development approach ⏳ ACTIVE
- **Quality Approach**: Test-first development with comprehensive documentation ⏳ REQUIRED
- **Success Measure**: Single command provisions dagorlad from clean state matching AWS Linux pattern ⏳ CRITERIA

**Current State Gap**:
- **AWS Linux (rivendell)**: Uses unified `provision.yml` with provider/platform parameters ✅ CONSISTENT
- **Vagrant Docker (dagorlad)**: Uses separate `vagrant up` + configuration commands ❌ INCONSISTENT
- **Problem**: Different command patterns create cognitive load and maintenance complexity ❌ ACTIVE ISSUE

**MVP Deliverables**:
1. Vagrant Provisioner Module (`provisioners/vagrant_docker-linux.yml`) ⏳ PENDING
2. Provider Extension (Update `provision.yml` parameter system) ⏳ PENDING  
3. Documentation Updates (`docs/create-vm.md`, `test/docker/README.md`) ⏳ PENDING
4. Test Suite (test-first approach with comprehensive validation) ⏳ PENDING

### Completed Infrastructure
- **Hetzner Cloud Linux**: Production-ready persistent development environment (~$4/month)
- **AWS Multi-Platform**: Both Linux and Windows implementations working
- **Cross-Provider Foundation**: Proven abstraction patterns across providers

### Current Infrastructure Status
- **Hetzner Cloud Linux**: Production-ready persistent development environment (~$4/month)
- **AWS Multi-Platform**: Linux and Windows implementations operational
- **Vagrant Testing**: Docker and Tart providers with unified variable management
- **Cross-Provider Patterns**: Proven abstraction and consistent automation patterns
