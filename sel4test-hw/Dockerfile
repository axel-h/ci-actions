# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

FROM sel4/sel4test-hw:latest

WORKDIR ci-scripts
COPY steps.sh ./
RUN chmod a+rx ./*

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libffi-dev \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/
RUN pip3 install junitparser PyGithub
WORKDIR /builds
COPY builds.yml \
     build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     ./

WORKDIR /workspace

ENTRYPOINT /ci-scripts/steps.sh