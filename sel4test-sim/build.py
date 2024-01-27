# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test build + simulation on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import argparse

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


def main(params: list) -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--dump', action='store_true')
    g.add_argument('--build', action='store_true')
    args = parser.parse_args(params)

    builds_yaml_file = os.path.join(os.path.dirname(__file__), "builds.yml")
    builds = load_builds(builds_yaml_file)

    if args.dump:
        pprint(builds)
        return 0

    # perform args.build as default
    return run_builds(builds, run_simulation)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
