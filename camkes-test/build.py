# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run CAmkES test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import json

from builds import Build, run_build_script, run_builds, load_builds, release_mq_locks, SKIP
from platforms import load_yaml, gh_output
from pprint import pprint


# See also builds.yml for how builds are split up in this test. We use the build
# matrix and filtering for the hardware builds, and an explicit list for the
# simulation builds.

# The only thing this really has in common with a "Build" is the "name" field.


class SimBuild():
    """Represents one simulation build + run."""

    def __init__(self, sim: dict):
        post = "_" + sim['iterator'][:1] if len(sim['iterator']) > 0 else ""
        self.name = sim['match'] + post
        self.__dict__.update(**sim)

    def __repr__(self) -> str:
        return f"SimBuild('{self.name}', " '{' \
            f" 'match': '{self.match}'," \
            f" 'exclude': '{self.exclude}'," \
            f" 'iterator': '{self.iterator}'" \
            ' })'


def run_build(manifest_dir: str, build: Build | SimBuild) -> int:
    """Run one CAmkES test. Can be either Build or SimBuild."""

    if isinstance(build, Build):
        app = apps[build.app]
        build.files = build.get_platform().image_names(build.get_mode(), "capdl-loader")
        build.settings['CAMKES_APP'] = build.app

        if app.get('has_cakeml'):
            build.settings['CAKEMLDIR'] = '/cakeml'
            build.settings['CAKEML_BIN'] = f"/cake-x64-{build.get_mode()}/cake"

        # remove parameters from setting that CMake does not use and thus would
        # raise a nasty warning
        if 'BAMBOO' in build.settings:
            del build.settings['BAMBOO']

        script = [
            ["../init-build.sh"] + build.settings_args(),
            ["ninja"],
            ["tar", "czf", f"../{build.name}-images.tar.gz", "images/"],
        ]
    elif isinstance(build, SimBuild):
        script = [
            ['bash', '-c',
             'cd ../projects/camkes/tests && '
             f"SEL4_CACHE_DIR=~/.sel4_cache/ "
             f"REGEX={build.match} "
             f"EXCLUDE_REGEX={build.exclude} "
             f"VERBOSE=-VV "
             f"RANGE={build.iterator} "
             'make run_tests'],
        ]
    else:
        print(f"Warning: unknown build type for {build.name}")

    return run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: Build) -> int:
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return SKIP

    build.success = apps[build.app]['success']
    script, final = build.hw_run('log.txt')

    return run_build_script(manifest_dir, build, script, final_script=final)


def build_filter(build: Build) -> bool:
    if not build.app:
        return False

    app = apps[build.app]
    plat = build.get_platform()

    if plat.name not in app['platforms']:
        return False
    if plat.arch == 'arm' and build.get_mode() not in app['arm_modes']:
        return False
    if plat.arch == 'x86' and build.get_mode() not in app['x86_modes']:
        return False

    return True


def sim_build_filter(build: SimBuild) -> bool:
    name = os.environ.get('INPUT_NAME')
    plat = os.environ.get('INPUT_PLATFORM')
    return (not name or build.name == name) and (not plat or plat == 'sim')


def to_json(builds: list[Build]) -> str:
    """Return a GitHub build matrix as GitHub output assignment."""

    matrix = {"include": [{"name": b.name, "platform": b.get_platform().name} for b in builds]}
    return "matrix=" + json.dumps(matrix)


# If called as main, run all builds from builds.yml
if __name__ == '__main__':
    yml = load_yaml(os.path.dirname(__file__) + "/builds.yml")
    apps = yml['apps']
    sim_builds = [SimBuild(s) for s in yml['sim']]
    hw_builds = load_builds(None, build_filter, yml)
    builds = [b for b in sim_builds if sim_build_filter(b)] + hw_builds

    if len(sys.argv) > 1 and sys.argv[1] == '--dump':
        pprint(builds)
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == '--matrix':
        gh_output(to_json(builds))
        sys.exit(0)
    elif len(sys.argv) > 1 and sys.argv[1] == '--hw':
        sys.exit(run_builds(builds, hw_run))
    elif len(sys.argv) > 1 and sys.argv[1] == '--post':
        release_mq_locks(builds)
        sys.exit(0)

    sys.exit(run_builds(builds, run_build))
