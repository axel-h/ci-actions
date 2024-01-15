# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run l4v C Parser test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os

from builds import run_build_script, run_builds, load_builds
from pprint import pprint


def run_cparser(manifest_dir: str, build) -> int:
    """Single run of the C Parser test, for one build definition"""

    script = [
        ["../init-build.sh"] + build.settings_args(),
        ["ninja", "kernel_all_pp_wrapper"],
        ["/c-parser/standalone-parser/c-parser", build.l4v_arch,
         '--underscore_idents', 'kernel/kernel_all_pp.c'],
    ]

    return run_build_script(manifest_dir, build, script)


def main(argv: list) -> int:

    builds = load_builds(os.path.dirname(__file__) + "/builds.yml")

    if len(argv) > 1 and argv[1] == '--dump':
        pprint(builds)
        return 0

    # by default, run all builds from builds.yml
    return run_builds(builds, run_cparser)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
