#=============================================================
# Dockerfile for OpenWPM
# See README.md for build & use instructions
#=============================================================

FROM ubuntu:24.04

#=============================================================
# Packages required for container setup
#=============================================================

RUN apt-get -qqy update && apt-get -qqy install -y sudo curl ca-certificates git build-essential

#=============================================================
# Copy OpenWPM source
#=============================================================
RUN mkdir -p /opt/OpenWPM
WORKDIR /opt/OpenWPM

# Copy the modern project layout
COPY . /opt/OpenWPM/

#=============================================================
# Add normal user with passwordless sudo, and switch
#=============================================================
RUN useradd -m -s /bin/bash -u 1000 user && \
    usermod -a -G sudo user && \
    echo 'ALL ALL = (ALL) NOPASSWD: ALL' >> /etc/sudoers

USER user
ENV PATH="/home/user/.local/bin:/home/user/conda/bin:${PATH}"

# Install modern conda env + Firefox 150+
RUN curl -fsSL https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh -o /tmp/miniforge.sh && \
    bash /tmp/miniforge.sh -b -p /home/user/conda && rm /tmp/miniforge.sh

RUN /home/user/conda/bin/conda env create -f environment.yaml -n openwpm && \
    /home/user/conda/bin/conda clean -a -y

RUN /home/user/conda/bin/conda run -n openwpm bash scripts/install-firefox.sh || true
