# Copyright 2021, Proofcraft Pty Ltd
# Copyright 2022, Axel Heider <axelheider@gmx.de>
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

FROM trustworthysystems/sel4:latest

ARG ACTION=repo-checkout
ARG SCRIPTS=/ci-scripts
ARG WORKSPACE=/workspace

# If we use debian:bullseye then this needs to be installed:
#   RUN apt-get update \
#       && apt-get install -y --no-install-recommends \
#          ssh curl git python-is-python3 python3-pip \
#       && apt-get clean autoclean \
#       && apt-get autoremove --yes \
#       && rm -rf /var/lib/{apt,dpkg,cache,log}/ \
#       && pip3 install PyGithub

RUN pip3 install PyGithub

COPY ${ACTION}/steps.sh scripts/* ${SCRIPTS}/
# check we got repo V1.21
RUN curl -o ${SCRIPTS}/repo https://storage.googleapis.com/git-repo-downloads/repo \
    && echo "72fc70040dad13f6f9e9d0de82beb98aff41fde0c9ed810c9251cb9500d3c8c0 ${SCRIPTS}/repo" \
       | sha256sum -c - \
    && chmod a+rx ${SCRIPTS}/*
ENV PATH "${SCRIPTS}:${PATH}"

WORKDIR ${WORKSPACE}

ENTRYPOINT steps.sh
