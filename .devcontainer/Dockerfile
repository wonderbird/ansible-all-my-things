# syntax=docker/dockerfile:1

# The latest version of the aws cli v2 is incompatible with alpine.
# The ansible packages require locale support, which is not available
# in slim.
#
# As a consequence, use the trixie python image instead.
#
FROM docker.io/python:trixie

# Valid options are:
#   - amd64 (Intel / AMD)
#   - arm64 (Apple Silicon / ARM)
#
ARG ARCH=arm64

RUN if [ "${ARCH}" != "arm64" ] && [ "${ARCH}" != "amd64" ]; then \
    echo "Error: ARCH must be either arm64 or amd64" && exit 1; \
fi

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
 RUN if [ "${ARCH}" = "arm64" ] ; then \
        AWS_ARCH="aarch64" ; \
    else \
        AWS_ARCH="x86_64" ; \
    fi \
    && gpg --import /tmp/aws/awscliv2-public-key.asc \
    && mkdir -p /tmp/awscli \
    && cd /tmp/awscli \
    && curl -o "awscliv2.zip" "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip" \
    && curl -o "awscliv2.sig" "https://awscli.amazonaws.com/awscli-exe-linux-${AWS_ARCH}.zip.sig" \
    && ls -la awscliv2.* \
    && gpg --verify --trust-model always awscliv2.sig awscliv2.zip \
    && unzip awscliv2.zip \
    && ./aws/install \
    && cd /root \
    && rm -rf /tmp/awscli \
    && aws --version

# Install Hetzner hcloud CLI
#
# Documentation:
#   - [hcloud CLI GitHub repository](https://github.com/hetznercloud/cli)
#
RUN mkdir -p /root/hcloud \
    && cd /root/hcloud \
    && wget "https://github.com/hetznercloud/cli/releases/download/v1.60.0/hcloud-linux-${ARCH}.tar.gz" -O "hcloud.tar.gz" \
    && tar -xvzf hcloud.tar.gz \
    && ln -s /root/hcloud/hcloud /usr/local/bin/hcloud \
    && cd /root \
    && hcloud version
