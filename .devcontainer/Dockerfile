# syntax=docker/dockerfile:1

# BuildKit Cache Mounts
#
#   The cache mounts improve build performance by persisting between builds.
#   Package lists are stored in the cache outside the image layers.
#   Thus, images stay small even without `rm -rf /var/lib/apt/lists/*` in each layer.

FROM ubuntu:26.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install build-time tools only (not carried into runtime image)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        git \
        gpg \
        gpg-agent \
        openssh-client \
        pipx \
        python3 \
        python3-venv \
        unzip \
        wget

COPY awscliv2-public-key.asc install-aws-cli.sh /tmp/installers/
RUN /bin/sh /tmp/installers/install-aws-cli.sh \
    && rm -rf /tmp/installers

COPY install-hcloud-cli.sh /tmp/installers/
RUN /bin/sh /tmp/installers/install-hcloud-cli.sh \
    && rm -rf /tmp/installers

COPY install-ansible-all-my-things.sh touch_to_force_repo_update.txt /tmp/installers/
RUN PATH="/root/.local/bin:$PATH" /bin/sh /tmp/installers/install-ansible-all-my-things.sh \
    && rm -rf /tmp/installers /root/ansible-all-my-things


FROM ubuntu:26.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base system packages (rarely change)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        locales \
        openssh-client \
        python3

# Install optional tools (can change independently)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        iputils-ping \
        jq \
        vim

# Copy CLI tools built in the builder stage
COPY --from=builder /usr/local/aws-cli /usr/local/aws-cli
RUN ln -s /usr/local/aws-cli/v2/current/bin/aws /usr/local/bin/aws \
    && ln -s /usr/local/aws-cli/v2/current/bin/aws_completer /usr/local/bin/aws_completer
COPY --from=builder /root/hcloud/hcloud /usr/local/bin/hcloud

# Copy ansible (pipx venv + wrappers) and galaxy collections
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.ansible /root/.ansible

ENV PATH="/root/.local/bin:$PATH"

# Setup directories (rarely changes)
RUN mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh \
    && mkdir /backup

CMD [ "bash" ]
