Feature: Claude Code role installs and verifies the Claude Code binary

  Background:
    Given the target host runs a supported Linux distribution
    And the variable "desktop_user_names" contains one or more user names

  Scenario: Successful installation on a supported architecture
    Given the host architecture is "x86_64" or "aarch64"
    And the GitHub Releases API is reachable
    And the Anthropic release manifest is reachable
    When the role is applied
    Then the claude binary exists in /home/<user>/.local/bin/ for each user
    And the binary checksum matches the expected checksum from the manifest
    And claude is added to PATH in /home/<user>/.bashrc for each user

  Scenario: Role is applied a second time on an already-installed system
    Given Claude Code is already correctly installed for each user
    And the binary checksum matches the current manifest
    When the role is applied again
    Then the play completes successfully
    And /home/<user>/.bashrc is unchanged for each user

  Scenario: Unsupported processor architecture
    Given the host architecture is not listed in claude_code_platform_map
    When the role is applied
    Then the play fails before downloading the installer
    And the failure message lists the supported architectures

  Scenario: GitHub Releases API is unreachable
    Given the GitHub Releases API is not reachable
    When the role is applied
    Then the play fails at the "Get latest Claude Code version" task
    And the installer is not downloaded
    And no binary is installed

  Scenario: Release manifest is unreachable
    Given the GitHub Releases API is reachable
    And the Anthropic release manifest URL is not reachable
    When the role is applied
    Then the play fails at the "Fetch Claude Code release manifest" task
    And the installer is not downloaded
    And no binary is installed

  Scenario: Release manifest has an unexpected JSON structure
    Given the GitHub Releases API is reachable
    And the release manifest does not contain an entry for the host platform
    When the role is applied
    Then the play fails at the "Extract expected Claude Code checksum" task
    And the installer is not downloaded
    And no binary is installed

  Scenario: Installed binary does not match the expected checksum
    Given the manifest is fetched successfully
    And the installer runs but produces a binary whose checksum differs from the manifest
    When the role is applied
    Then the binary is deleted from /home/<user>/.local/bin/ for each affected user
    And the play fails with a message showing both the expected and actual checksums
    And claude is not added to PATH in /home/<user>/.bashrc for any affected user

  Scenario: Installer runs but does not create the binary
    Given the manifest is fetched successfully
    And the installer exits without creating /home/<user>/.local/bin/claude
    When the role is applied
    Then the play fails indicating the binary is absent
    And claude is not added to PATH in /home/<user>/.bashrc

  Scenario: File system error when computing the binary checksum
    Given the manifest is fetched successfully
    And the installer runs successfully
    And the stat module cannot read the installed binary
    When the role is applied
    Then the play fails at the "Compute SHA256 of installed Claude Code binary" task
    And the binary is not deleted

  Scenario Outline: One user passes verification, another does not
    Given the manifest is fetched successfully
    And the installer runs successfully for all users
    And the binary for "<failing_user>" has a checksum that does not match the manifest
    When the role is applied
    Then the binary for "<failing_user>" is deleted
    And the play fails with a message naming "<failing_user>"
    And claude is not added to PATH for "<failing_user>"

    Examples:
      | failing_user                      |
      | first user in desktop_user_names  |
      | second user in desktop_user_names |
