#!/usr/bin/env python3
"""Patch RISC-V tests Makefiles for modern GCC compatibility.

This script is IDEMPOTENT - safe to run multiple times without corrupting files.

Fixes:
- GCC 12+: Adds _zicsr extension to -march flags (CSR instructions)
- GCC 10+: Adds -fcommon to fix multiple definition errors (tohost/fromhost)
- Adds picolibc specs and warning suppressions for legacy C code
"""
import os
import re
import sys

def patch_benchmarks_makefile(filepath):
    """Patch benchmarks/Makefile for modern GCC."""
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    original = content

    # Target: RISCV_GCC_OPTS line
    # We want: --specs=picolibc.specs -march=rv64gc_zicsr -mabi=lp64 -DPREALLOCATE=1 ... -fcommon -Wno-implicit-int -Wno-implicit-function-declaration

    # Check if already fully patched
    if all(flag in content for flag in ['rv64gc_zicsr', '-fcommon', '-Wno-implicit-int', '--specs=picolibc.specs']):
        print(f"Already patched: {filepath}")
        return False

    # Pattern to match the RISCV_GCC_OPTS line
    gcc_opts_pattern = r'(RISCV_GCC_OPTS\s*\?=\s*)([^\n]+)'

    def fix_gcc_opts(match):
        prefix = match.group(1)
        opts = match.group(2)

        # Add picolibc specs if missing
        if '--specs=picolibc.specs' not in opts:
            opts = '--specs=picolibc.specs ' + opts

        # Fix march flag - ensure _zicsr is present
        opts = re.sub(r'-march=rv64gc(?!_zicsr)', '-march=rv64gc_zicsr', opts)

        # Add -mabi=lp64 if missing
        if '-mabi=' not in opts:
            opts = opts.replace('-march=rv64gc_zicsr', '-march=rv64gc_zicsr -mabi=lp64')

        # Replace -fno-common with -fcommon, or add -fcommon
        if '-fno-common' in opts:
            opts = opts.replace('-fno-common', '-fcommon')
        elif '-fcommon' not in opts:
            opts += ' -fcommon'

        # Add warning suppressions if missing
        if '-Wno-implicit-int' not in opts:
            opts += ' -Wno-implicit-int'
        if '-Wno-implicit-function-declaration' not in opts:
            opts += ' -Wno-implicit-function-declaration'

        return prefix + opts

    content = re.sub(gcc_opts_pattern, fix_gcc_opts, content)

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched: {filepath}")
        return True
    else:
        print(f"No changes needed: {filepath}")
        return False


def patch_isa_makefile(filepath):
    """Patch isa/Makefile for modern GCC."""
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return False

    with open(filepath, 'r') as f:
        content = f.read()

    original = content

    # Check if already fully patched
    if all(x in content for x in ['rv32g_zicsr', 'rv64g_zicsr', '-fcommon', '--specs=picolibc.specs']):
        print(f"Already patched: {filepath}")
        return False

    # Fix march flags for both 32-bit and 64-bit (only if _zicsr not already present)
    content = re.sub(r'-march=rv32g(?!_zicsr)', '-march=rv32g_zicsr', content)
    content = re.sub(r'-march=rv64g(?!_zicsr)', '-march=rv64g_zicsr', content)

    # Fix RISCV_GCC_OPTS line
    gcc_opts_pattern = r'(RISCV_GCC_OPTS\s*\?=\s*)([^\n]+)'

    def fix_gcc_opts(match):
        prefix = match.group(1)
        opts = match.group(2)

        # Add picolibc specs if missing
        if '--specs=picolibc.specs' not in opts:
            opts = '--specs=picolibc.specs ' + opts

        # Add -fcommon if missing
        if '-fcommon' not in opts:
            opts += ' -fcommon'

        return prefix + opts

    content = re.sub(gcc_opts_pattern, fix_gcc_opts, content)

    if content != original:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Patched: {filepath}")
        return True
    else:
        print(f"No changes needed: {filepath}")
        return False


def main():
    ariane_root = os.path.expanduser('~/openpiton/piton/design/chip/tile/ariane/')

    bench_makefile = os.path.join(ariane_root, 'tmp/riscv-tests/benchmarks/Makefile')
    isa_makefile = os.path.join(ariane_root, 'tmp/riscv-tests/isa/Makefile')

    patched = False
    patched |= patch_benchmarks_makefile(bench_makefile)
    patched |= patch_isa_makefile(isa_makefile)

    if patched:
        print("\nPatching complete. Run 'make clean' before rebuilding.")
    else:
        print("\nAll files already patched or not found.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
