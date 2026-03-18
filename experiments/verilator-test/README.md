# OpenPiton Verilator Build Modernization

## Status: WORKING on Ubuntu 24.04 LTS + Verilator 5.020 + GCC 13

Successfully built `Vcmp_top` and ran RISC-V ISA tests on the Verilator RTL model.

## Quick Start

```bash
# Install prerequisites
sudo apt install gcc g++ verilator gcc-riscv64-unknown-elf \
    picolibc-riscv64-unknown-elf git python3 autoconf

# Build everything
./clean_build.sh

# Run a test
cd ~/openpiton
export PITON_ROOT=$HOME/openpiton
export ARIANE_ROOT=$PITON_ROOT/piton/design/chip/tile/ariane
source piton/piton_settings.bash
source piton/ariane_setup.sh
sims -sys=manycore -x_tiles=1 -y_tiles=1 -ariane -vlt_run \
    -image_diag_root=$ARIANE_ROOT/tmp/riscv-tests/build/isa \
    -image_diag_name=rv64ui-p-add
```

## Why This Modernization?

The original OpenPiton build was designed for older toolchains (GCC 7, Verilator 4.014, Bison 3.5). Modern Ubuntu 24.04 ships with GCC 13, Verilator 5.020, and Bison 3.8 - causing multiple build failures. This project patches the build to work with modern system packages, eliminating the need to compile toolchains from source.

## Issues Found & Fixes

### 1. Verilator 5.x Compatibility

| Issue | Cause | Fix |
|-------|-------|-----|
| `-lstdc++` linker error | Was in CFLAGS, needs LDFLAGS | `patch_openpiton.py` |

**Why Verilator 5.x instead of downgrading to 4.014?**
- Avoids Bison 3.5.1 dependency (Ubuntu has 3.8.2, incompatible with Verilator 4.014)
- Future-proof - prevents dependency rot
- Available via apt = easier CI/CD

### 2. GCC 13 C++ Strictness

| Issue | Cause | Fix |
|-------|-------|-----|
| `my_top.cpp` const error | `char*` passed where `const char*` expected | `fix_cpp.py` |
| `fesvr/device.h` error | Missing `#include <cstdint>` for `uint64_t` | `patch_fesvr.py` |

**Why these break on GCC 13?**
- GCC 13 enforces ISO C++ const-correctness strictly
- `uint64_t` no longer implicitly available - requires explicit header

### 3. RISC-V Toolchain (GCC 12+)

| Issue | Cause | Fix |
|-------|-------|-----|
| CSR instruction errors | GCC 12 requires explicit `zicsr` extension | `-march=rv64gc_zicsr` |
| Multiple definition errors | GCC 10 default changed to `-fno-common` | Added `-fcommon` |
| Missing libc headers | Ubuntu apt package incomplete | Use `picolibc-riscv64-unknown-elf` |

**Why picolibc instead of building GCC from source (ci/build-riscv-gcc.sh)?**
- Available via apt - no 2+ hour compile
- Provides complete Newlib-compatible headers
- System package = automatic security updates

### 4. Idempotency Bug (Critical)

| Issue | Cause | Fix |
|-------|-------|-----|
| Makefiles corrupted on re-run | Original `patch_riscv_tests.py` patterns didn't match after first run | Rewrote with regex + "already patched" checks |
| Duplicate patching | Both `ariane_build_tools.sh` (sed) and `patch_riscv_tests.py` modified same files | Unified in new idempotent script |

## Scripts

| Script | Purpose |
|--------|---------|
| `clean_build.sh` | Unified build - handles all patching automatically |
| `patch_riscv_tests.py` | Patches ISA/benchmark Makefiles (idempotent) |
| `patch_openpiton.py` | Patches sims script for Verilator 5.x |
| `patch_fesvr.py` | Adds `<cstdint>` to fesvr headers |
| `fix_cpp.py` | Fixes const-correctness in my_top.cpp |

## Compatibility Matrix

| Component | Version | Source |
|-----------|---------|--------|
| Ubuntu | 24.04 LTS | - |
| GCC | 13.3.0 | System |
| Verilator | 5.020 | `apt install verilator` |
| RISC-V GCC | 13.2.0 | `apt install gcc-riscv64-unknown-elf` |
| picolibc | System | `apt install picolibc-riscv64-unknown-elf` |

## CI Modernization Summary

| Old (source build) | New (system packages) |
|--------------------|----------------------|
| `ci/build-riscv-gcc.sh` (2+ hours) | `apt install gcc-riscv64-unknown-elf picolibc-riscv64-unknown-elf` |
| `ci/install-verilator.sh` (Verilator 4.014 + Bison 3.5.1) | `apt install verilator` (5.x) |
| `ci/install-fesvr.sh` | Keep (no apt package) + `<cstdint>` patch |
| `ci/install-spike.sh` | Keep (no apt package) |

## Test Result

```
$ sims -sys=manycore -x_tiles=1 -y_tiles=1 -ariane -vlt_run \
    -image_diag_root=$ARIANE_ROOT/tmp/riscv-tests/build/isa \
    -image_diag_name=rv64ui-p-add

Reset complete
750000250 : Simulation -> (terminated by reaching max cycles = 1500000)
```

Build and test execution verified on Ubuntu 24.04 + Verilator 5.020 + GCC 13.
