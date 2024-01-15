# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run rumprun test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os

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


def main(argv: list) -> int:
    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(argv) > 1 and argv[1] == '--dump':
        pprint(builds)
        return 0

    if len(argv) > 1 and argv[1] == '--hw':
        return run_builds(builds, hw_run)

    if len(argv) > 1 and argv[1] == '--post':
        release_mq_locks(builds)
        return 0

    # by default, run all builds from builds.yml
    return run_builds(builds, run_build)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
