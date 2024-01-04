#!/bin/bash
#
# Copyright 2020, Data61, CSIRO (ABN 41 687 119 230)
#
# SPDX-License-Identifier: BSD-2-Clause
#

echo "Arch: $INPUT_ARCH"
echo "Comp: $INPUT_COMPILER"
echo "MCS: $INPUT_MCS"
echo "HYP: $INPUT_HYP"

set -eu

gcc_cfg=""
llvm_triple=""
case "${INPUT_ARCH}" in
    ARM|ARM_HYP)
        gcc_cfg="AARCH32"
        llvm_triple="arm-linux-gnueabi"
        ;;
    AARCH64)
        gcc_cfg="AARCH64"
        llvm_triple="aarch64-linux-gnu"
        ;;
    RISCV32)
        gcc_cfg="RISCV32"
        # the 64-bit toolchain can build for 32-bit also.
        llvm_triple="riscv64-unknown-elf"
        ;;
    RISCV64)
        gcc_cfg="RISCV64"
        llvm_triple="riscv64-unknown-elf"
        ;;
    IA32|X64)
        # just use the standard host compiler
        ;;
    *)
        echo "Unknown ARCH '${INPUT_ARCH}'"
        exit 1
        ;;
esac

toolchain_flags=""
toolchain_file="${INPUT_COMPILER}.cmake"
case "${INPUT_COMPILER}" in
    gcc)
        if [ ! -z "${gcc_cfg}" ]; then
            toolchain_flags="-D${gcc_cfg}=TRUE"
        fi
        ;;
    clang|llvm)
        if [ ! -z "${llvm_triple}" ]; then
            toolchain_flags="-DTRIPLE=${llvm_triple}"
        fi
        if [ "${INPUT_COMPILER}" == "clang" ]; then
            toolchain_file="llvm.cmake"
        fi
        ;;
    *)
        echo "Unknown COMPILER '${INPUT_COMPILER}'"
        exit 1
        ;;
esac
toolchain_flags="-DCMAKE_TOOLCHAIN_FILE=${toolchain_file} ${toolchain_flags}"

config_file="configs/${INPUT_ARCH}_verified.cmake"
build_folder=build
flags=""
variant=""

case "${INPUT_MCS}" in
    true)
        if [ ! -z "${variant}" ]; then
            variant="${variant}-"
        fi
        variant="${variant}MCS"
        # Use a dedicated config file if available, otherwise just use the
        # default config and enable MCS.
        try_config_file="configs/${INPUT_ARCH}_MCS_verified.cmake"
        if [ -f "${try_config_file}" ]; then
            config_file="${try_config_file}"
        else
            flags="${flags} KernelIsMCS"
        fi
        ;;
    false)
        # nothing
        ;;
    *)
        echo "Unknown INPUT_MCS '${INPUT_MCS}'"
        exit 1
esac

case "${INPUT_HYP}" in
    true)
        if [ ! -z "${variant}" ]; then
            variant="${variant}-"
        fi
       variant="${variant}HYP"

        case "${INPUT_ARCH}" in
            ARM_HYP)
                # implicit
                ;;
            ARM|AARCH64)
                flags="${flags} KernelArmHypervisorSupport"
                ;;
            RISCV32|RISCV64)
                # ToDo: do we have KernelRiscvHypervisorSupport ?
                echo "HYP is not supported on RISCV"
                exit 1
                ;;
            X64)
                flags="${flags} KernelVTX"
                ;;
            IA32)
                echo "HYP is not supported on IA32"
                exit 1
                ;;
            *)
                echo "Unknown INPUT_ARCH for HYP: '${INPUT_ARCH}'"
                exit 1
        esac
        ;;
    false)
        # nothing
        ;;
    *)
        echo "Unknown INPUT_HYP '${INPUT_HYP}'"
        exit 1
esac

# add all flags
extra_params=""
for flag in ${flags}; do
    extra_params="${extra_params} -D${flag}=TRUE"
done

# Unfortunately, CMake does not halt with a nice and clear error if the config
# file does not exist. Instead, it logs an error that it could not process the
# file and continues as if the file was empty. This causes some rather odd
# errors later, so it's better to fail here with a clear message.
if [ ! -f "${config_file}" ]; then
    echo "missing config file '${config_file}'"
    exit 1
fi

variant_info=""
if [ ! -z "${variant}" ]; then
    variant_info=" (${variant})"
    build_folder="${build_folder}-${variant}"
fi

echo "::group::Run CMake${variant_info}"
( # run in sub shell
    set -x
    cmake -G Ninja -B ${build_folder} -C ${config_file} ${toolchain_flags} ${extra_params}
)
echo "::endgroup::"

echo "::group::Run Ninja${variant_info}"
( # run in sub shell
    set -x
    ninja -C ${build_folder} kernel.elf
)
echo "::endgroup::"
