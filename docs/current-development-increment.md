# Current Development Increment: Unified Vagrant Docker Provisioning

## Product Owner Context
**Role**: Experienced Scrum Product Owner
**Business Driver**: Urgent need for consistent provisioning commands across cloud VMs and Vagrant VMs
**Timeline**: 2-3 days delivery
**Quality Approach**: Test-first development with up-to-date documentation, accepting rough proof of concept

## MVP Definition

### Business Goal
Enable unified provisioning command for Vagrant Docker environment (dagorlad) that matches the AWS Linux pattern (rivendell), improving user experience and code maintainability.

### Current State Analysis
- **AWS Linux (rivendell)**: Uses `ansible-playbook provision.yml --extra-vars "provider=aws platform=linux" --vault-password-file ansible-vault-password.txt`
- **Vagrant Docker (dagorlad)**: Uses `vagrant up` + separate `ansible-playbook configure-linux.yml` command
- **Gap**: Different command patterns create cognitive load and maintenance complexity

### MVP Scope: Unified Vagrant Docker Provisioning

**Target Command Pattern** (extending existing provider/platform pattern):
```bash
ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" --vault-password-file ansible-vault-password.txt
```

**Must-Have Deliverables**:

1. **Vagrant Provisioner Module** (`provisioners/vagrant_docker-linux.yml`)
   - Handles `vagrant up` execution via Ansible
   - Manages Vagrant lifecycle (up/status checking)
   - Integrates with existing inventory system
   - Follows same pattern as existing provisioners (`provisioners/aws-linux.yml`, `provisioners/hcloud-linux.yml`)

2. **Provider Extension** (Update existing `provision.yml`)
   - Extend existing provider/platform parameter system
   - Support `provider=vagrant_docker platform=linux` parameters
   - Reuse existing `configure-linux.yml` integration
   - Maintain backward compatibility with existing providers

3. **Documentation Updates** (enable easy extension of create-vm.md)
   - Update `docs/create-vm.md` to include `vagrant_docker` as provider option
   - Update `test/docker/README.md` with new unified command
   - Document `provider=vagrant_docker platform=linux` parameter usage
   - Add Vagrant-specific prerequisites and limitations

4. **Test Suite**
   - Test-first approach: Write tests before implementation
   - Verify provisioning command works end-to-end with provider/platform parameters
   - Validate inventory integration and variable loading
   - Test idempotency (can run multiple times safely)

### Acceptable Quality Trade-offs

**What's Acceptable**:
- Basic error handling (fail fast, clear error messages)
- Manual steps documented if needed for edge cases
- Rough proof of concept implementation
- Limited to dagorlad environment only (no other Vagrant providers)

**Non-Negotiable**:
- Tests must pass (green tests top priority)
- Documentation must be current and accurate
- Command pattern must match AWS Linux approach

### Success Criteria

**Primary Success**: 
Command `ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" --vault-password-file ansible-vault-password.txt` successfully provisions dagorlad environment from clean state.

**Validation Tests**:
1. Clean environment → run command → dagorlad accessible via SSH
2. Re-run command → idempotent (no errors, no duplicate resources)
3. Command follows same pattern as existing `provision-aws-linux.yml`

**User Experience Success**:
- Single command provisioning (no need to remember `vagrant up` + separate configure)
- Consistent with other environments
- Clear error messages if something fails

### Timeline: 2-3 Days

**Day 1**: Test-first development
- Write test specifications
- Implement core `provisioners/vagrant_docker-linux.yml` logic
- Test provider/platform parameter integration

**Day 2**: Integration and refinement
- Integrate with inventory system
- Test end-to-end functionality
- Fix integration issues

**Day 3**: Documentation and validation
- Update `docs/create-vm.md` with vagrant_docker provider option
- Update `test/docker/README.md` with unified command
- Final validation testing
- Memory bank updates

### Technical Implementation Notes

**Key Integration Points**:
- Extend existing `provision.yml` parameter system (provider/platform pattern)
- Reuse existing `configure-linux.yml` playbook integration
- Leverage existing inventory structure (`inventories/vagrant_docker.yml`)
- Maintain compatibility with existing Vagrant configuration
- Use same vault and SSH key patterns as production environments

**Risk Mitigation**:
- Follow existing provisioner pattern (`provisioners/aws-linux.yml`, `provisioners/hcloud-linux.yml`)
- Test frequently during development
- Keep Vagrant-specific logic isolated in provisioner module
- Ensure backward compatibility with existing provider/platform combinations

### Out of Scope (Future Increments)

- Other Vagrant providers (Tart, VirtualBox)
- Advanced error handling and edge cases
- Vagrant destroy command unification
- Performance optimization
- Advanced Vagrant configuration options

## Definition of Done

- [ ] `ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" --vault-password-file ansible-vault-password.txt` provisions dagorlad successfully
- [ ] All tests pass (test-first approach followed)
- [ ] Documentation updated: `docs/create-vm.md` includes vagrant_docker provider option
- [ ] Documentation updated: `test/docker/README.md` uses unified command
- [ ] Code follows existing patterns and conventions
- [ ] Memory bank updated with current state
- [ ] Manual validation completed
- [ ] Ready for future extension to other Vagrant providers

---

**Product Owner Approval**: Ready for implementation
**Sprint Goal**: Unified provisioning command for Vagrant Docker environment
**Business Value**: Improved developer experience and reduced maintenance complexity