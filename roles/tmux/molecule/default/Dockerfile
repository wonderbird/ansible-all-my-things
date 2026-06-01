FROM docker.io/library/ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq \
    && apt-get install -y -qq --no-install-recommends \
       python3 sudo python3-apt ca-certificates git fontconfig unzip
