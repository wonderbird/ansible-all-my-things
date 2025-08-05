# Unified Vagrant Docker Provisioning

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

**What's Acceptable for MVP**:
- Basic error handling (fail fast, clear error messages)
- Manual steps documented if needed for edge cases
- Rough proof of concept implementation
- Limited to dagorlad environment only (no other Vagrant providers)

**Non-Negotiable**:
- **Working command is top priority** (confirmed with Product Owner)
- Command pattern must match AWS Linux approach
- Documentation must be current and accurate
- Test automation is secondary to working implementation

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

## Development Plan (Milestone-Based)

### Priority Strategy
**Confirmed with Product Owner**: Focus on getting the basic command working first. Test automation is secondary priority if time constraints arise.

### Milestone 1: Core Command Implementation (Day 1 - Priority 1)
**Goal**: Get the basic unified command working

**Task 1.1: Create Vagrant Provisioner Module** (2-3 hours)
- **File**: `provisioners/vagrant_docker-linux.yml`
- **Implementation**:
  - Change directory to `test/docker/` (existing structure)
  - Execute `vagrant up` command via Ansible
  - Add basic error handling for vagrant failures
  - Follow existing provisioner patterns from `provisioners/hcloud-linux.yml`
- **Technical Notes**:
  - Use `shell` module with `chdir: test/docker` parameter
  - Handle `vagrant up` idempotency (check if already running)

**Task 1.2: Verify Template Routing** (1 hour)
- **Test**: Run `ansible-playbook provision.yml --extra-vars "provider=vagrant_docker platform=linux" --vault-password-file ansible-vault-password.txt`
- **Validation**: 
  - Confirm routing to new provisioner works (`provisioners/vagrant_docker-linux.yml`)
  - Confirm routing to existing configure works (`configure-linux.yml`)
- **Expected Behavior**: No template routing errors

**Task 1.3: Manual End-to-End Validation** (1 hour)
- **Test Protocol**: Clean environment → run unified command → verify dagorlad accessible
- **Validation Steps**:
  - SSH connectivity test: `ssh vagrant@dagorlad_ip -p 2223`
  - Basic whoami check: `ansible linux -m shell -a 'whoami' --extra-vars "ansible_user=gandalf"`
- **Success Criteria**: Command completes without errors and dagorlad is reachable

### Milestone 2: Integration & Testing (Day 2 - Priority 2)
**Goal**: Ensure reliability and proper integration

**Task 2.1: Test Idempotency** (2 hours)
- Verify command can run multiple times safely without errors
- Test with existing vagrant environment (should not fail)
- Validate no duplicate resources created

**Task 2.2: Inventory Integration Validation** (1 hour)
- Verify `ansible-inventory --graph` shows dagorlad correctly
- Test variable loading from `inventories/group_vars/vagrant_docker/vars.yml`
- Confirm SSH key and vault integration works

**Task 2.3: Automated Test Creation** (2-3 hours)
- Copy and adapt existing `test/test_vagrant_linux_provisioning.md`
- Create automated test script based on existing validation steps
- Focus on core functionality validation

### Milestone 3: Documentation & Completion (Day 3 - Priority 3)
**Goal**: Complete the MVP with documentation

**Task 3.1: Documentation Updates** (2 hours)
- Update `docs/create-vm.md` to include `vagrant_docker` as provider option
- Update `test/docker/README.md` with unified command usage
- Document `provider=vagrant_docker platform=linux` parameter pattern

**Task 3.2: Memory Bank Updates** (1 hour)
- Update `progress.md` with completed milestone
- Update `activeContext.md` with current implementation status
- Document lessons learned and next steps

**Task 3.3: Final Validation** (1 hour)
- Complete end-to-end testing with fresh environment
- Verify all Definition of Done criteria met
- Prepare for Product Owner acceptance

### Risk Mitigation Strategy
- **Keep existing structure**: Use `test/docker/` directory as-is to minimize risk
- **Follow existing patterns**: Base implementation on `provisioners/hcloud-linux.yml`
- **Manual validation first**: Ensure command works before automated testing
- **Incremental approach**: Get basic functionality working, then enhance

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