# Docker provider VM image: systemd-enabled Ubuntu with sshd, root/password
# auth. Run with `docker run --privileged ...` so systemd can manage cgroups.
#
# Package policy: this image is a *managed-node* surrogate — a local stand-in
# for a fresh AWS/Hetzner cloud VM that Ansible connects to and configures. It
# is NOT the control node (.devcontainer image, which carries ansible/aws-cli/
# hcloud/git/gpg). Keep this image to the minimum a cloud VM presents so local
# tests stay at least as strict as the real target: a role that forgets a tool
# prereq must fail HERE, not slip through because the image happened to ship it.
#
# Therefore tool prereqs (curl, git, unzip, gpg, ...) are NOT baked in — each
# role installs its own (e.g. roles/java installs zip/unzip/curl). curl in
# particular is deliberately absent: it was once added to paper over roles that
# assumed an ambient curl; those roles instead use ansible.builtin.get_url
# (native, idempotent, fails loud) or install curl themselves.
#
# Exception — ca-certificates IS kept: it is shared TLS trust *substrate*, not a
# tool. ~10 roles use get_url over HTTPS and rely on the system CA store;
# installing it per-role would duplicate it everywhere (DRY), and every real
# cloud Ubuntu image ships it. systemd/sshd/sudo/python3 are likewise the
# connection substrate Ansible cannot bootstrap over.
FROM ubuntu:24.04

ARG DOCKER_ROOT_PASSWORD

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        systemd \
        systemd-sysv \
        openssh-server \
        sudo \
        dbus \
        python3 \
        ca-certificates \
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
