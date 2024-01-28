# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

"""
Parse builds.yml and run CAmkES test on each of the build definitions.

Expects seL4-platforms/ to be co-located or otherwise in the PYTHONPATH.
"""

import sys
import os
import argparse
import json

import builds
import platforms
import pprint


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


def run_build(manifest_dir: str, build: builds.Build | SimBuild) -> int:
    """Run one CAmkES test. Can be either Build or SimBuild."""

    if isinstance(build, builds.Build):
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

    return builds.run_build_script(manifest_dir, build, script)


def hw_run(manifest_dir: str, build: builds.Build) -> int:
    """Run one hardware test."""

    if build.is_disabled():
        print(f"Build {build.name} disabled, skipping.")
        return builds.SKIP

    build.success = apps[build.app]['success']
    script, final = build.hw_run('log.txt')

    return builds.run_build_script(manifest_dir, build, script, final_script=final)


def build_filter(build: builds.Build) -> bool:
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


def gh_output_matrix(param_name: str, build_list: list[builds.Build]) -> None:
    matrix_builds = [{"name": b.name,
                      "platform": b.get_platform().name
                     }
                     for b in build_list]
    # GitHub output assignment
    matrix_json = json.dumps({"include": matrix_builds})
    platforms.gh_output(f"{param_name}={matrix_json}")


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
    yml = platforms.load_yaml(builds_yaml_file)
    apps = yml['apps']
    sim_builds = [SimBuild(s) for s in yml['sim']]
    hw_builds = builds.load_builds(None, build_filter, yml)
    build_list = [b for b in sim_builds if sim_build_filter(b)] + hw_builds

    if args.dump:
        pprint.pprint(build_list)
        return 0

    if args.matrix:
        gh_output_matrix("matrix", build_list)
        return 0

    if args.hw:
        return builds.run_builds(build_list, hw_run)

    if args.post:
        builds.release_mq_locks(build_list)
        return 0

    # perform args.build as default
    return builds.run_builds(build_list, run_build)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
