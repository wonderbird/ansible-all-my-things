# Building and verifying the toolchain Docker image

[Container Structure Tests](https://github.com/GoogleContainerTools/container-structure-test)
verify correctness of the Dockerfile.

## Building the toolchain Docker image locally

```shell
docker build --tag "ansible-toolchain" .
```

## Running container structure tests locally

Follow the
[Container Structure Tests](https://github.com/GoogleContainerTools/container-structure-test)
documentation to install the `container-structure-test` command.

Run the tests:

```shell
container-structure-test test --image ansible-toolchain:latest --config ./tests.yaml
```

## More details in pipeline

The GitHub Action building the Docker image shows details:
[.github/workflows/docker-publish.yml](.github/workflows/docker-publish.yml).
