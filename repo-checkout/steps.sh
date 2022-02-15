#!/bin/bash
#
# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause
#

set -e

echo "::group::Setting up"

mkdir -p ~/bin
curl https://storage.googleapis.com/git-repo-downloads/repo > ~/bin/repo
# check we got repo V1.21
echo "72fc70040dad13f6f9e9d0de82beb98aff41fde0c9ed810c9251cb9500d3c8c0 $(readlink -f ~)/bin/repo" | sha256sum -c -
chmod a+x ~/bin/repo
PATH=~/bin:$PATH

pip3 install -U PyGithub

echo "::endgroup::"

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
