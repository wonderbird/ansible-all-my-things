# syntax=docker/dockerfile:1

# BuildKit Cache Mounts
#
#   The cache mounts improve build performance by persisting between builds.
#   Package lists are stored in the cache outside the image layers.
#   Thus, images stay small even without `rm -rf /var/lib/apt/lists/*` in each layer.

# The latest version of the aws cli v2 is incompatible with alpine.
# The ansible packages require locale support, which is not available
# in slim.
#
# As a consequence, use the trixie python image instead.
#
FROM docker.io/python:trixie

# Install base system packages (rarely change)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        locales \
        locales-all

# Install optional tools (can change independently)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        iputils-ping \
        jq \
        vim

# Setup directories (rarely changes)
RUN mkdir -p /root/.ssh \
    && chmod 700 /root/.ssh \
    && mkdir /backup

COPY awscliv2-public-key.asc install-aws-cli.sh /tmp/installers/
RUN /bin/sh /tmp/installers/install-aws-cli.sh \
    && rm -rf /tmp/installers

COPY install-hcloud-cli.sh /tmp/installers/
RUN /bin/sh /tmp/installers/install-hcloud-cli.sh \
    && rm -rf /tmp/installers

COPY install-ansible-all-my-things.sh touch_to_force_repo_update.txt /tmp/installers/
RUN /bin/sh /tmp/installers/install-ansible-all-my-things.sh \
    && rm -rf /tmp/installers

CMD [ "bash" ]
