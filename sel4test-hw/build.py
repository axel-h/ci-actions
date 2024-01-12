# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run sel4test hardware builds and runs on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import argparse
import json
import itertools

from builds import Build, run_build_script, run_builds, load_builds, junit_results
from builds import release_mq_locks, SKIP
from platforms import Platform, gh_output
from pprint import pprint


def hw_build(manifest_dir: str, build: Build) -> int:
    """Run one hardware build."""

    if build.get_platform().name == "RPI4":
        # The Raspberry Pi 4B model that is used for hardware testing has 4GB
        # of RAM, which we must specify when building the kernel.
        build.settings["RPI4_MEMORY"] = "4096"

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja"],
        ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
        ["cp", "kernel/kernel.elf", f"../{build.name}-kernel.elf"]
    ]

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build) -> int:
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    script, final = build.hw_run(junit_results)

    return run_build_script(manifest_dir, build, script, final_script=final, junit=True)


def build_filter(build: Build) -> bool:
    plat = build.get_platform()

    if plat.no_hw_build:
        return False

    if plat.arch == 'arm':
        # ToDo: why is release for hikey in aarch64 arm_hyp mode is not supported
        if build.is_hyp() and build.get_mode() == 64 and build.is_release() and \
           plat.name == 'HIKEY':
            return False

        # MCS exclusions:
        # No MCS + SMP for platforms with global timer for now (see seL4/seL4#513)
        if plat.name == 'SABRE' and build.is_smp() and build.is_mcs():
            return False
        # SCHED_CONTEXT_0014 fails on TX1, TX2 and ODROID_C4: https://github.com/seL4/seL4/issues/928
        if plat.name in ['TX1', 'TX2', 'ODROID_C4'] and \
           build.is_mcs() and build.is_smp() and build.is_hyp() and build.is_clang():
            return False
        # CACHEFLUSH0001 fails on ODROID_XU4: https://github.com/seL4/sel4test/issues/80
        if plat.name == 'ODROID_XU4' and build.is_debug() and build.is_mcs() and \
           build.is_hyp() and build.is_clang() and build.get_mode() == 32:
            return False
        # IMX8MM_EVK is failing multicore tests for MCS + SMP:
        if plat.name == 'IMX8MM_EVK' and build.is_mcs() and build.is_smp():
            return False

        # HYP/SMP exclusions:
        # IMX8MQ_EVK and ZYNQMPs are failing multicore tests for SMP + HYP + clang
        # see also https://github.com/seL4/sel4test/issues/44
        if plat.name in ['IMX8MQ_EVK', 'ZYNQMP', 'ZYNQMP106'] and \
           build.is_hyp() and build.is_smp() and build.is_clang():
            return False

    if plat.arch == 'x86':
        # ToDo: explant why we don't do VTX for SMP or verification
        if build.is_hyp() and (build.is_smp() or build.is_verification()):
            return False

    if plat.arch == 'riscv':
        # see also https://github.com/seL4/seL4/issues/1160
        if plat.name == 'HIFIVE' and build.is_clang() and build.is_smp() and build.is_release():
            return False

    # run NUM_DOMAINS > 1 tests only on release builds
    if build.is_domains() and not build.is_release():
        return False

    return True


def gh_output_matrix(param_name: str, builds: list[Build]) -> None:
    build_list = []
    # Loop over all the different platforms of the build list. Using
    # set-comprehension " { ... for ... } " instead of list-comprehension
    # " [ ... for ... ] " eliminates duplicates automatically.
    for plat in {b.get_platform() for b in builds}:

        # ignore all platforms that can't tested or not even be built
        if plat.no_hw_test or plat.no_hw_build:
            continue

        variants = {"compiler": ["gcc", "clang"]}
        if (plat.arch == 'x86'):
            variants["mode"] = plat.modes

        # create builds for all combination from the variants matrix
        for vals in itertools.product(*(variants.values())):
            build_variant = {"platform": plat.name,
                             "march": plat.march,
                             **dict(zip(variants.keys(), vals))
                            }
            build_list.append(build_variant)

    # GitHub output assignment
    matrix_json = json.dumps({"include": build_list})
    gh_output(f"{param_name}={matrix_json}")


def main(params: list) -> int:
    parser = argparse.ArgumentParser()
    g = parser.add_mutually_exclusive_group()
    g.add_argument('--dump', action='store_true')
    g.add_argument('--matrix', action='store_true')
    g.add_argument('--hw', action='store_true')
    g.add_argument('--post', action='store_true')
    g.add_argument('--build', action='store_true')
    args = parser.parse_args(params)

    builds_yaml_file = os.path.join(os.path.dirname(__file__), "builds.yml")
    builds = load_builds(builds_yaml_file, filter_fun=build_filter)

    if args.dump:
        pprint(builds)
        return 0

    if args.matrix:
        gh_output_matrix("matrix", builds)
        return 0

    if args.hw:
        run_builds(builds, hw_run)
        return 0

    if args.post:
        release_mq_locks(builds)
        return 0

    # perform args.build as default
    return run_builds(builds, hw_build)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
