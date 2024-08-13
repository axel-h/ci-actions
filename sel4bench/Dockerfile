# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

FROM sel4/sel4bench:latest

WORKDIR ci-scripts
COPY steps.sh ./
RUN chmod a+rx ./*

WORKDIR /builds
COPY builds.yml \
     build.py \
     seL4-platforms/platforms.yml \
     seL4-platforms/platforms.py \
     seL4-platforms/builds.py \
     ./

WORKDIR /workspace

ENTRYPOINT /ci-scripts/steps.sh
