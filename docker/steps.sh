#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

CP_DEST=$1

if [[ ! -d ${CP_DEST} }}; then
    mkdir -p ${CP_DEST}
fi

checkout-manifest.sh
cd l4v/tools/c-parser
make standalone-cparser
cd standalone-parser
cp -vr c-parser ARM ARM_HYP AARCH64 RISCV64 X64 ${CP_DEST}/
