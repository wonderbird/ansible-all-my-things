# syntax=docker/dockerfile:1

ARG ARCH=aarch64
#ARG ARCH=x86_64

# The latest version of the aws cli v2 is incompatible with alpine.
# The ansible packages require locale support, which is not available
# in slim.
# Thus we use the trixie python image instead.
FROM docker.io/python:trixie

RUN apt-get update \
#    && apt-get install -y --no-install-recommends \
#        curl \
#        gpg \
#        jq \
#        locales \
#        locales-all \
#        openssh-client \
#        unzip \
#        vim \
    && rm -rf /var/lib/apt/lists/*
