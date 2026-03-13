# OpenPiton Verilator Build & Toolchain Validation

## Status: COMPLETED (Migrating to Native Linux)

## Goal
Build the cycle-accurate RTL model of OpenPiton (`Vcmp_top`) using Verilator and prepare the cross-compilation toolchain for bare-metal RISC-V programs.

## Scripts & Tools

### `repair_sims.py`
- **What it does:** Edits the OpenPiton `sims` Perl script to permanently remove modern Verilator 5.x flags (`-Wno-TIMESCALEMOD`, `--no-timing`).
- **Why we use it:** The OpenPiton source accidentally merges syntax meant for newest Verilators with an older codebase that fails parsing them.

### `fix_cpp.py`
- **What it does:** Modifies `piton/tools/verilator/my_top.cpp` by converting `char*` declaration in `init_jbus_model_call` to `const char*`.
- **Why we use it:** Modern C++ compilers (like GCC 13+ on Ubuntu 24.04) enforce strict const-correctness. The original 2018 code violated this, halting the build.

### `patch_riscv_tests.py`
- **What it does:** Iterates through `tmp/riscv-tests` Makefiles and strategically inserts the `_zicsr` architecture extension flag (`-march=rv64gc_zicsr`). It also suppresses implicit int/declaration warnings.
- **Why we use it:** Modern versions of GCC separated CSR instructions into a distinct module (`zicsr`). Older C code like Dhrystone failed compiling without it due to modernized compiler strictness.

## Major Dependency Challenges & Resolutions

This phase exposed significant toolchain fragility across two decades of software (2018-2024).

1. **Verilator Version Mismatch (Precompiled Headers)**
   - **Issue:** Initially attempted with Verilator 5.x on Ubuntu. RTL compiled to C++, but standard linker `make` failed due to unpredictable Precompiled Header (PCH) behaviors unique to Verilator 5.
   - **Fix:** Downgraded to **Verilator 4.014**, which provides the exact stability OpenPiton was originally validated against.

2. **Bison 3.8.x Conflict**
   - **Issue:** Ubuntu 24.04 ships with Bison 3.8+, which deprecates syntax heavily utilized by Verilator 4.014's parser.
   - **Fix:** Manually compiled and installed **Bison 3.5.1** from source to bridge the gap.

3. **RISC-V Toolchain Missing Libraries (Ubuntu APT)**
   - **Issue:** The standard `gcc-riscv64-unknown-elf` package on Ubuntu `apt` is fragmented and lacks necessary Newlib headers (`string.h`, `libc-header-start.h`), failing all OpenPiton benchmarks.
   - **Fix:** Abandoned `apt`. Transitioned manually to the **xPack RISC-V Toolchain (v15.2.0-1)**, an independently maintained binary distribution ensuring complete Newlib compatibility.

## Result
We successfully acquired the compiled executable RTL (`obj_dir/Vcmp_top`) and documented exactly how the RISC-V build chain fails on modern OSs.

## Next Steps
To guarantee clean builds that align exactly with the OpenPiton maintainers, we are migrating this entire project away from WSL to a **Native Linux (Ubuntu 22.04) Environment**, utilizing all the scripts/patches created in this folder during the final repository build!
