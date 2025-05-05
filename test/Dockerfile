# Testsystem for my Ansible playbooks
#
# This container only exposes the SSH port. If you want to test services, then consider forwarding the corresponding
# ports via an SSH tunnel.
#
# Keep this file in sync with
# https://raw.githubusercontent.com/wonderbird/ansible-for-devops/refs/heads/main/Dockerfile.Ubuntu
#
# Adopted from https://circleci.com/blog/ssh-into-docker-container/
#
FROM ubuntu:24.10
ENV container=docker

RUN apt-get update && apt-get install -y --no-install-recommends \
    apt-utils \
    cron \
    curl \
    git \
    gnupg \
    hostname \
    openssh-server \
    procps \
    python3 \
    python3-packaging \
    sudo \
    systemd \
    util-linux-extra \
    vim \
    which \
    && rm -rf /var/lib/apt/lists/*

# Enable systemd and configure it properly for container use
RUN (cd /lib/systemd/system/sysinit.target.wants/; for i in *; do [ $i == systemd-tmpfiles-setup.service ] || rm -f $i; done); \
    # rm -f /lib/systemd/system/multi-user.target.wants/*; \
    rm -f /etc/systemd/system/*.wants/*; \
    rm -f /lib/systemd/system/local-fs.target.wants/*; \
    rm -f /lib/systemd/system/sockets.target.wants/*udev*; \
    rm -f /lib/systemd/system/sockets.target.wants/*initctl*; \
    rm -f /lib/systemd/system/basic.target.wants/*; \
    systemctl enable ssh;

# Ensure that the SSH server has a consistent host key.
COPY ./ssh_host_keys/* /etc/ssh/
RUN chmod 600 /etc/ssh/*_key \
    && chmod 644 /etc/ssh/*_key.pub

# Setup the SSH server for user "vagrant", which is used by Vagrant by default.
# Enable public key authentication.
# Add the vagrant user to the sudo group.
# Allow sudo without password.
RUN sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config \
    && useradd -m -s /bin/bash vagrant \
    && usermod -aG sudo vagrant \
    && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
    && mkdir -p /run/sshd

COPY ./ssh_user_key/id_ecdsa.pub /home/vagrant/.ssh/authorized_keys
RUN mkdir -p /home/vagrant/.ssh \
    && chmod 700 /home/vagrant/.ssh \
    && chmod 600 /home/vagrant/.ssh/authorized_keys \
    && chown -R vagrant:vagrant /home/vagrant/.ssh

EXPOSE 22

# Use systemd as the entrypoint instead of the service command
ENTRYPOINT ["/lib/systemd/systemd"]