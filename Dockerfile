# Ubuntu 24.04 LTS. The digest is the manifest list resolved on 2026-11-04.
# Miniforge is pinned to release 26.9.4-1. The installer bytes are not
# digest-pinned in this file. There is no passwordless sudo and no root
# runtime user. Firefox installation is not hidden with "|| true".

FROM ubuntu:24.04@sha256:fe81560990fae86dc4743202b2cb4d3df98d0bcf949173cecef15ce1127ef852 AS base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        wget \
        bzip2 \
        tar \
        gzip \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -s /bin/bash -u 1000 user \
    && mkdir -p /opt/OpenWPM \
    && chown user:user /opt/OpenWPM

WORKDIR /opt/OpenWPM

FROM base AS build

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
USER user
ENV PATH="/home/user/conda/bin:${PATH}"

RUN curl -fsSL -o /tmp/miniforge.sh \
        https://github.com/conda-forge/miniforge/releases/download/26.9.4-1/Miniforge3-Linux-x86_64.sh \
    && bash /tmp/miniforge.sh -b -p /home/user/conda \
    && rm /tmp/miniforge.sh

COPY --chown=user:user . /opt/OpenWPM

RUN conda env create -f environment.yaml -n openwpm \
    && conda clean -a -y \
    && conda run -n openwpm bash scripts/install-firefox.sh

FROM base AS runtime

COPY --from=build --chown=user:user /home/user/conda /home/user/conda
COPY --from=build --chown=user:user /opt/OpenWPM /opt/OpenWPM

USER user
ENV PATH="/home/user/conda/bin:${PATH}"
WORKDIR /opt/OpenWPM

CMD ["/home/user/conda/bin/conda", "run", "--no-capture-output", "-n", "openwpm", "python", "scripts/minimal-crawl.py", "--check"]
