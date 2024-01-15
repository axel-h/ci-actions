# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context for this Dockerfile is the repo root

ARG ACTION=camkes-unit
ARG SCRIPTS=/ci-scripts

FROM trustworthysystems/camkes:latest
ARG ACTION
ARG SCRIPTS

WORKDIR ${SCRIPTS}
COPY scripts/*.sh \
     ${ACTION}/steps.sh \
     ./
RUN chmod a+rx ./*
ENV PATH="${SCRIPTS}:${PATH}"

WORKDIR /workspace

ENTRYPOINT ${SCRIPTS}/steps.sh
