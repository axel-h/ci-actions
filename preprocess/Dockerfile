# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# The context of this Dockerfiles is the repo root (../)

ARG SCRIPTS=/ci-scripts
ARG ACTION=preprocess

FROM trustworthysystems/sel4:latest
ARG SCRIPTS
ARG ACTION

COPY --from=sel4/cparser-builder /c-parser /c-parser

WORKDIR ${SCRIPTS}
COPY ${ACTION}/steps.sh \
     ${ACTION}/make_munge.sh \
     ${ACTION}/test_munge.sh \
     scripts/* ./
RUN chmod a+rx ./*
ENV  PATH "${SCRIPTS}:${PATH}"

WORKDIR /workspace

ENTRYPOINT ${SCRIPTS}/steps.sh
