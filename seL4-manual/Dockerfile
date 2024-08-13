# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

FROM sel4/sel4-manual:latest

WORKDIR ci-scripts
COPY steps.sh ./
RUN chmod a+rx ./*

WORKDIR /workspace

ENTRYPOINT /ci-scripts/steps.sh
