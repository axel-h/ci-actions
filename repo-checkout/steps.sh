#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Repo checkout"

export REPO_MANIFEST="${INPUT_MANIFEST}"
export MANIFEST_URL="https://github.com/seL4/${INPUT_MANIFEST_REPO}"
checkout-manifest.sh

fetch-branches.sh

echo "::endgroup::"

XML="$(repo manifest -r --suppress-upstream-revision | nl-escape.sh)"

if [ -z "${GITHUB_OUTPUT}" ]; then
  echo "Warning: GITHUB_OUTPUT not set"
  GITHUB_OUTPUT="github.output"
fi
echo "xml=${XML}" >> ${GITHUB_OUTPUT}
