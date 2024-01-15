# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG SCRIPTS=/ci-scripts
ARG ACTION=tutorials

FROM trustworthysystems/camkes:latest
ARG SCRIPTS
ARG ACTION

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN pip3 install junitparser PyGithub

WORKDIR ${SCRIPTS}
COPY ${ACTION}/steps.sh \
     scripts/* \
     ./
RUN chmod a+rx ./*
ENV PATH "${SCRIPTS}:${PATH}"

WORKDIR /builds
COPY ${ACTION}/builds.yml \
     ${ACTION}/build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     /builds/

WORKDIR /github/home
# nothing added here, just create folder

WORKDIR /workspace

ENTRYPOINT ${SCRIPTS}/steps.sh
