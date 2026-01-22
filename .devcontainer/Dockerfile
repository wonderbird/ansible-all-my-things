# syntax=docker/dockerfile:1

# The latest version of the aws cli v2 is incompatible with alpine.
# The ansible packages require locale support, which is not available
# in slim.
#
# As a consequence, use the trixie python image instead.
FROM docker.io/python:trixie

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        iputils-ping \
        jq \
        locales \
        locales-all \
        vim \
    && rm -rf /var/lib/apt/lists/*
