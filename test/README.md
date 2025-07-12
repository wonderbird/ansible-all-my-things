# Tests

## Manual Tests

At the moment, automatic tests are missing 😔.

The reason is that this project has been in a "proof of concept phase" until 2025-07-11.

Now the project is transitioning from a "Genesis" stage to a more mature "Custom Built" stage [wardley2020], [harrer2023]. Thus, existing manual tests are documented in this directory. Automated tests are planned.

## Test systems

The test systems use Vagrant.

- [docker](docker/README.md): Vagrant with Docker Provider
- [tart](tart/README.md): Vagrant with Tart Provider

### A note on incompatibility

The `Vagrantfile`s in each folder skip incompatible playbooks by tags.

Linux homebrew does not support the arm64 (Apple Silicon) architecture.
The tag `not-supported-on-vagrant-arm64` is intended for playbooks incompatible
with this architecture.

The Docker Ubuntu image does not support the XFCE desktop environment.
Because the playbook works for the Tart provider, it is tagged with
`not-supported-on-vagrant-docker`.

## References

[wardley2020] S. Wardley, “Wardley Maps,” Learn Wardley Mapping. Accessed: Sep. 29, 2022. [Online]. Available: [https://learnwardleymapping.com/book/](https://learnwardleymapping.com/book/)

[harrer2023] M. Harrer, “Evolutionäre Softwarequalität,” presented at the OOP Konferenz, Feb. 09, 2023. [Online]. Available: [https://sigs-new.scoocs.co/event/63/stage/206/session/1729](https://sigs-new.scoocs.co/event/63/stage/206/session/1729)
