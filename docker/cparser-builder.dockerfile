# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause

# ---[ sel4/cparser-builder ]---
#
# Builder container for the l4v standalone C parser
# see the preprocess action for an example how to use

# The context of this Dockerfiles is the repo root (../)

ARG CP_DEST=/c-parser/standalone-parser

FROM trustworthysystems/l4v:latest AS builder
ARG CP_DEST

WORKDIR ${SCRIPTS}
COPY scripts/checkout-manifest.sh \
     ${ACTION}/steps.sh \
     ./
RUN chmod a+rx ./*
ENV SCRIPTS=${SCRIPTS}
ENV PATH="${SCRIPTS}:${PATH}"

WORKDIR ${CP_DEST}
# nothing added here, just create folder

WORKDIR /workspace

RUN ${SCRIPTS}/steps.sh ${CP_DEST}


FROM scratch
ARG CP_DEST
WORKDIR ${CP_DEST}
COPY --from=builder ${CP_DEST} ./
