# Copyright 2021, Proofcraft Pty Ltd
#
# SPDX-License-Identifier: BSD-2-Clause

import sys
from platforms import platforms, gh_output


def main(argv: list) -> int:
    if len(argv) != 2:
        return 1

    plat = platforms.get(argv[1].upper())
    if plat:
        gh_output(f"march={plat.march}")
        return 0

    print(f"Unknown platform {argv[1]}")
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
