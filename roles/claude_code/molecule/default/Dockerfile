FROM docker.io/library/ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
       python3 sudo git curl ca-certificates pipx \
    && rm -rf /var/lib/apt/lists/*
