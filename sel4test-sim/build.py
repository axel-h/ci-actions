# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test build + simulation on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os

from builds import Build, run_build_script, run_builds, load_builds, junit_results
from pprint import pprint


def run_simulation(manifest_dir: str, build: Build) -> int:
    """Run one simulation build and test."""

    expect = '"%s" {exit 0} timeout {exit 1}' % build.success

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["bash", "-c",
         f"expect -c 'spawn ./simulate; set timeout 1200; expect {expect}' | tee {junit_results}"]
    ]

    return run_build_script(manifest_dir, build, script, junit=True)


def main(argv: list) -> int:
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(argv) > 1 and argv[1] == '--dump':
        pprint(builds)
        return 0

    # by default, run all builds from builds.yml
    return run_builds(builds, run_simulation)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
