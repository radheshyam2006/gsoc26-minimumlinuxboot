#!/usr/bin/env python3
import os

def patch_file(filepath, search_and_replace_list):
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} (not found)")
        return
    with open(filepath, 'r') as f:
        content = f.read()
    
    modified = False
    for old, new in search_and_replace_list:
        if old in content:
            content = content.replace(old, new)
            modified = True
            print(f"Found and replaced target in {filepath}")
    
    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Successfully updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")

ariane_root = os.path.expanduser('~/openpiton/piton/design/chip/tile/ariane/')

# 1. Patch Benchmarks Makefile
# Fixes: zicsr extension and lazy C code warnings
bench_makefile = os.path.join(ariane_root, 'tmp/riscv-tests/benchmarks/Makefile')
patch_file(bench_makefile, [
    ('-march=rv64gc_zicsr', '-march=rv64gc_zicsr'), # Identity check
    ('RISCV_GCC_OPTS ?= -DPREALLOCATE=1', 'RISCV_GCC_OPTS ?= -march=rv64gc_zicsr -mabi=lp64 -DPREALLOCATE=1'),
    ('-ffast-math -fno-common', '-ffast-math -fno-common -Wno-implicit-int -Wno-implicit-function-declaration')
])

# 2. Patch ISA Makefile
# Fixes: zicsr extension for both 32-bit and 64-bit tests
# IMPORTANT: Remove any previously added -march from RISCV_GCC_OPTS first
isa_makefile = os.path.join(ariane_root, 'tmp/riscv-tests/isa/Makefile')
patch_file(isa_makefile, [
    ('-march=rv64gc_zicsr', ''), # Remove the bad patch if exists
    ('-march=rv32g', '-march=rv32g_zicsr'),
    ('-march=rv64g', '-march=rv64g_zicsr')
])

# 3. Handle specific assembly files in benchmarks if needed
# The error "extension `zicsr` required" also happens in crt.S and syscalls.c
# Usually adding it to GCC flags is enough, but some tools pass flags directly to as.

print("Patching complete. Please run 'make clean' before rebuilding.")
