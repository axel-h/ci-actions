# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG SCRIPTS=/ci-scripts
ARG ACTION=eL4-manual

FROM trustworthysystems/sel4:latest
ARG SCRIPTS
ARG ACTION

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       doxygen \
       texlive \
       texlive-fonts-extra \
       texlive-latex-extra \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && rm -rf /var/lib/{apt,dpkg,cache,log}/

WORKDIR ${SCRIPTS}
COPY scripts/*.sh \
     ${ACTION}/steps.sh \
     ./
RUN chmod a+rx ./*
ENV PATH="${SCRIPTS}:${PATH}"

WORKDIR /workspace

ENTRYPOINT ${SCRIPTS}/steps.sh
