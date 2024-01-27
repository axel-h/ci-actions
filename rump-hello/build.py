# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run rumprun test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import argparse

from builds import Build, run_build_script, run_builds, load_builds, sim_script
from builds import release_mq_locks, SKIP
from pprint import pprint


def adjust_build(build: Build):
    build.files = build.get_platform().image_names(build.get_mode(), "roottask")
    # remove parameters from setting that CMake does not use and thus would
    # raise a nasty warning
    if 'BAMBOO' in build.settings:
        del build.settings['BAMBOO']


def run_build(manifest_dir: str, build: Build) -> int:
    """Run one rumprun-hello test."""

    adjust_build(build)

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"]
    ]

    if build.req == 'sim':
        script.append(sim_script(build.success))
    else:
        script.append(["tar", "czf", f"../{build.name}-images.tar.gz", "images/"])

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build) -> int:
    """Run one hardware test."""

    adjust_build(build)

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    script, final = build.hw_run('log.txt')

    return run_build_script(manifest_dir, build, script, final_script=final)


def main(params: list) -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--dump', action='store_true')
    g.add_argument('--hw', action='store_true')
    g.add_argument('--post', action='store_true')
    g.add_argument('--build', action='store_true')
    args = parser.parse_args(params)

    builds_yaml_file = os.path.join(os.path.dirname(__file__), "builds.yml")
    builds = load_builds(builds_yaml_file)

    if args.dump:
        pprint(builds)
        return 0

    if args.hw:
        return run_builds(builds, hw_run)

    if args.post:
        release_mq_locks(builds)
        return 0

    # perform args.build as default
    return run_builds(builds, run_build)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
