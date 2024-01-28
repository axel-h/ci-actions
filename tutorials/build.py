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
import json

from builds import Build, load_builds, run_build_script, run_builds, junit_results
from platforms import load_yaml, gh_output
from pprint import pprint


def run_simulation(manifest_dir: str, build: Build) -> int:
    """Run one tutorial test."""

    script = [
        ["bash", "-c",
         f"../projects/sel4-tutorials/test.py --app={build.app} "
         f"--config={build.get_platform().name.lower()} | tee {junit_results}"]
    ]

    return run_build_script(manifest_dir, build, script, junit=True)


def build_filter(build: Build) -> bool:
    return build.app not in disable_app_for.get(build.get_platform().name, [])


def to_json(builds: list) -> str:
    """Return a GitHub build matrix as GitHub output assignment.

    Basically just returns a list of build names that we can then
    filter on."""

    matrix = {"include": [{"name": b.name} for b in builds]}
    return "matrix=" + json.dumps(matrix)


def main(params: list) -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--dump', action='store_true')
    g.add_argument('--matrix', action='store_true')
    g.add_argument('--build', action='store_true')
    args = parser.parse_args(params)

    yml = load_yaml(os.path.dirname(__file__) + "/builds.yml")
    disable_app_for = yml['disable_app_for']
    builds = load_builds(None, build_filter, yml)

    if args.dump:
        pprint(builds)
        return 0

    if args.matrix:
        gh_output(to_json(builds))
        return 0

    # perform args.build as default
    return run_builds(builds, run_simulation)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
