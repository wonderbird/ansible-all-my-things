# Building and verifying the toolchain Docker image

[Container Structure Tests](https://github.com/GoogleContainerTools/container-structure-test)
verify correctness of the Dockerfile.

## Building the toolchain Docker image locally

Run from the repository root:

```shell
docker build --tag "ansible-toolchain" .devcontainer/
```

## Running container structure tests locally

Follow the
[Container Structure Tests](https://github.com/GoogleContainerTools/container-structure-test)
documentation to install the `container-structure-test` command.

Run from the repository root:

```shell
container-structure-test test --image ansible-toolchain:latest --config .devcontainer/tests.yaml
```

## More details in pipeline

The GitHub Action building the Docker image shows details:
[.github/workflows/docker-publish.yml](../../../../.github/workflows/docker-publish.yml).
