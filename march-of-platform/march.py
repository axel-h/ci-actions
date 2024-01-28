# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

import sys
#import argparse
from platforms import platforms, gh_output


def main(params: list) -> int:
    #parser = argparse.ArgumentParser()
    #g = parser.add_mutually_exclusive_group()
    #args = parser.parse_args()

    if len(params) != 2:
        return 1

    arg = params[1]
    plat = platforms.get(arg.upper())
    if plat:
        gh_output(f"march={plat.march}")
        return 0

    print(f"Unknown platform: '{arg}'")
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
