# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run CAmkES VM test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import shutil
import argparse
import datetime

from builds import Build, run_build_script, run_builds, load_builds, release_mq_locks, SKIP
from pprint import pprint


# See also builds.yml for how builds are split up in this test. We use the build
# matrix and filtering for the hardware builds, and an explicit list for the
# simulation builds.

# The only thing this really has in common with a "Build" is the "name" field.

def run_build(build_list: builds.Build) -> int:
    """Run one CAmkES VM build."""

    def setup(build)
        plat = build.get_platform()
        build.files = plat.image_names(build.get_mode(), "capdl-loader")
        build.settings['CAMKES_VM_APP'] = build.app or build.name
        # if vm_platform is set, the init-build.sh script expects a different platform name.
        if build.vm_platform:
            build.settings['PLATFORM'] = build.vm_platform

        # remove parameters from setting that CMake does not use and thus would
        # raise a nasty warning
        if 'BAMBOO' in build.settings:
            del build.settings['BAMBOO']
        if plat.arch == 'x86':
            del build.settings['PLATFORM']

    # if vm_platform is set, the init-build.sh script expects a different platform name.
    if build.vm_platform:
        build.settings['PLATFORM'] = build.vm_platform
        return [
            ["../init-build.sh"] + build.settings_args(),
            ["ninja"],
            ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
        ]


    # run form the current working directory
    base_dir = os.getcwd()
    print()
    sys.stdout.flush()

    for build in build_list:
        info = f"build {run.name}"
        script = setup(build)
        builds.printc_start(info)
        ret = builds.run_script_from_build_subdir(base_dir, script)
        builds.printc_end(info)

    return ret


def run_sim(manifest_dir: str, build: builds.Build) -> int:

    if not plat.has_simulation or plat.name == 'PC99':
        return 0

    script = [
        sim_script(build.success, failure=build.error
    ]

    return builds.run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: builds.Build) -> int:
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return builds.SKIP

    plat = build.get_platform()
    build.files = plat.image_names(build.get_mode(), "capdl-loader")

    script, final = build.hw_run('log.txt')

    return builds.run_build_script(manifest_dir, build, script, final_script=final)


def main(params: list) -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--dump', action='store_true')
    g.add_argument('--hw', action='store_true')
    g.add_argument('--post', action='store_true')
    g.add_argument('--build', action='store_true')
    args = parser.parse_args(params)

    builds_yaml_file = os.path.join(os.path.dirname(__file__), "builds.yml")
    build_list = builds.load_builds(builds_yaml_file)

    if args.dump:
        pprint.pprint(build_list)
        return 0

    if args.hw:
        return builds.run_builds(build_list, hw_run)

    if args.post:
        builds.release_mq_locks(build_list)
        return 0

    # perform args.build as default
    return run_build(build_list)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
