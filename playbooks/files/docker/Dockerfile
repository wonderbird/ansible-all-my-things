# Docker provider VM image: systemd-enabled Ubuntu with sshd, root/password
# auth. Run with `docker run --privileged ...` so systemd can manage cgroups.
FROM ubuntu:24.04

ARG DOCKER_ROOT_PASSWORD

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        systemd \
        systemd-sysv \
        openssh-server \
        sudo \
        dbus \
        python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /etc/ssh/sshd_config.d \
    && printf 'PermitRootLogin yes\nPasswordAuthentication yes\n' \
        > /etc/ssh/sshd_config.d/10-root-password-auth.conf \
    && echo "root:${DOCKER_ROOT_PASSWORD}" | chpasswd \
    && systemctl enable ssh

# systemd ignores SIGTERM; SIGRTMIN+3 triggers a clean shutdown so
# `docker stop` doesn't have to wait for the kill timeout.
STOPSIGNAL SIGRTMIN+3

ENTRYPOINT ["/sbin/init"]
