# syntax=docker/dockerfile:1

# The latest version of the aws cli v2 is incompatible with alpine.
# The ansible packages require locale support, which is not available
# in slim.
#
# As a consequence, use the trixie python image instead.
#
FROM docker.io/python:trixie

ARG ARCH=aarch64

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        iputils-ping \
        jq \
        locales \
        locales-all \
        vim \
    && rm -rf /var/lib/apt/lists/*

 # Install AWS CLI v2
 #
 # Documentation:
 #   - [AWS CLI install and update instructions](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
 #
 COPY awscliv2-public-key.asc /tmp/aws/awscliv2-public-key.asc
 RUN gpg --import /tmp/aws/awscliv2-public-key.asc \
    && mkdir -p /tmp/awscli \
    && cd /tmp/awscli \
    && curl -o "awscliv2.zip" "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip" \
    && curl -o "awscliv2.sig" "https://awscli.amazonaws.com/awscli-exe-linux-${ARCH}.zip.sig" \
    && ls -la awscliv2.* \
    && gpg --verify --trust-model always awscliv2.sig awscliv2.zip \
    && unzip awscliv2.zip \
    && ./aws/install \
    && cd /root \
    && rm -rf /tmp/awscli \
    && aws --version
