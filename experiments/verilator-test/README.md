# OpenPiton+Ariane Verilator Build Modernization

## Status:  WORKING — `rv64ui-p-add` PASSES

```
Info: spc(0) thread(0) Hit Good trap
18562250: Simulation -> PASS (HIT GOOD TRAP)
```

Tested on: Ubuntu 24.04 LTS / GCC 13.3.0 / Verilator 5.020 / RISC-V GCC 13.2.0

---

## Quick Start (Fresh Ubuntu 24.04 LTS)

```bash
# 1. Install all dependencies (single command)
sudo apt install -y gcc g++ verilator gcc-riscv64-unknown-elf \
    picolibc-riscv64-unknown-elf git python3 autoconf \
    device-tree-compiler make

# 2. Clone and enter repo
git clone --recurse-submodules https://github.com/radheshyam2006/openpiton.git
cd openpiton

# 3. Build everything
./clean_build.sh

# 4. Set up environment
export PITON_ROOT=$PWD
export ARIANE_ROOT=$PITON_ROOT/piton/design/chip/tile/ariane
source piton/piton_settings.bash
source piton/ariane_setup.sh

# 5. Build Verilator simulation model (~8-10 min)
sims -sys=manycore -x_tiles=1 -y_tiles=1 -ariane -vlt_build

# 6. Run RISC-V ISA test
sims -sys=manycore -x_tiles=1 -y_tiles=1 -ariane -vlt_run \
    -precompiled -asm_diag_name=rv64ui-p-add
```

Expected output:
```
Reset complete
Info: spc(0) thread(0) Hit Good trap
18562250: Simulation -> PASS (HIT GOOD TRAP)
```

---

## Compatibility Matrix

| Component | Old (broken) | New (working) | Source |
|---|---|---|---|
| Ubuntu | 20.04 | 24.04 LTS | — |
| GCC (host) | 7 | 13.3.0 | `apt` |
| Verilator | 4.014 + Bison 3.5.1 | 5.020 | `apt install verilator` |
| RISC-V GCC | source build (2+ hrs) | 13.2.0 | `apt install gcc-riscv64-unknown-elf` |
| libc for RISC-V | missing (broke benchmarks) | picolibc | `apt install picolibc-riscv64-unknown-elf` |
| Device Tree Compiler | source build | system | `apt install device-tree-compiler` |
| fesvr | source build | source build + patch | no apt package |
| spike | source build | source build | no apt package |

---

## Issues Found and Fixed

### Issue 1 — Verilator 5.x linker flag location

**Symptom:** Linker error during `vlt_build` — `-lstdc++` in wrong position.

**Cause:** `-lstdc++` was in `CFLAGS` inside the `sims` script. Verilator 5.x
passes flags differently — linker flags must be in `LDFLAGS`.

**Fix:** `patch_openpiton.py` moves `-lstdc++` from CFLAGS to LDFLAGS.

**Why Verilator 5.x instead of downgrading to 4.014?**
Verilator 4.014 requires Bison 3.5.1. Ubuntu 24.04 ships Bison 3.8.2 which
is incompatible — downgrading would require building Bison from source too,
continuing the dependency rot cycle.

---

### Issue 2 — GCC 13 C++ const-correctness (`my_top.cpp`)

**Symptom:** Build error: `char*` passed where `const char*` expected.

**Cause:** GCC 13 strictly enforces ISO C++ const-correctness. One declaration
in `piton/tools/verilator/my_top.cpp` used `char*` for a string literal.

**Fix:** `fix_cpp.py` — changes `char*` → `const char*`. Clean, correct fix.

---

### Issue 3 — GCC 13 missing `<cstdint>` in fesvr (`device.h`)

**Symptom:** `uint64_t` undeclared in `fesvr/device.h`.

**Cause:** GCC 13 no longer implicitly includes `<cstdint>`. The old fesvr
header relied on it being pulled in transitively.

**Fix:** `patch_fesvr.py` — adds `#include <cstdint>` explicitly.

---

### Issue 4 — RISC-V GCC 12+: missing `_zicsr` extension

**Symptom:** CSR instructions rejected by compiler (`csrr`, `csrw`, etc.).

**Cause:** GCC 12+ separates CSR instructions into a distinct `zicsr`
extension. Benchmark Makefiles only specified `-march=rv64gc`.

**Fix:** `patch_riscv_tests.py` — adds `_zicsr` to all march flags:
`-march=rv64gc` → `-march=rv64gc_zicsr -mabi=lp64`

---

### Issue 5 — GCC 10+: `-fno-common` default change

**Symptom:** Multiple definition errors in compiled benchmark objects.

**Cause:** GCC 10 changed the default from `-fcommon` to `-fno-common`.
Some benchmark objects had multiply-defined global symbols that previously
relied on the old default being tolerant.

**Fix:** Added `-fcommon` to affected Makefile targets in `patch_riscv_tests.py`.

---

### Issue 6 — Ubuntu apt RISC-V package lacks Newlib headers

**Symptom:** Every benchmark fails at compile time — missing `string.h`,
`stdio.h`, etc.

**Cause:** The `gcc-riscv64-unknown-elf` apt package is fragmented — it
provides the compiler but not the Newlib C library headers. This is why
`ci/build-riscv-gcc.sh` builds GCC from source: it bundles Newlib.

**Fix:** `apt install picolibc-riscv64-unknown-elf` provides complete
Newlib-compatible headers as a system package. No source build needed.

---

### Issue 7 — Idempotency bug in `patch_riscv_tests.py`

**Symptom:** Running `clean_build.sh` twice corrupts the RISC-V test Makefiles.

**Cause:** The original script used simple string substitution with no check
for whether the patch had already been applied. Running it twice would
double-apply the flags, producing invalid Makefile syntax.

**Fix:** Rewrote with regex matching and "already patched" guards. The script
is now safe to run any number of times.

---

### Issue 8 — Boot ROM rv64 sign-extension bug (RTL fix)

**Symptom:** Simulation produces `FAIL(TIMEOUT)`. Instruction trace shows
core executing only 10 instructions then hitting `WFI` at `0xfff101004c`
and sleeping forever. Core never fetches from `0x80000000`.

**Full trace (all 10 instructions executed):**
```
0xfff1010000  addiw        ← boot ROM start
0xfff1010004  c.li
0xfff1010006  csrr a0, mhartid
0xfff101000a  auipc a1, 0
0xfff101000e  addi a1, a1, 0x76
0xfff1010012  jr a1        ← jumps to 0xfff1010040 (wrong!)
0xfff1010040  csrr a0, mhartid
0xfff1010044  auipc a1, 0
0xfff1010048  addi a1, a1, 0x3c
0xfff101004c  WFI          ← sleeps here forever
```

**Root cause:** `bootrom.S` computes DRAM_BASE as:
```assembly
li s0, 1
slli s0, s0, 31    # on rv64: produces 0xffffffff80000000, NOT 0x80000000
```
On rv64, shifting `1` left by 31 bits produces a value that RISC-V
sign-extends in a 64-bit register: `0xffffffff80000000`. The jump to
this unmapped address causes an Instruction Access Fault, which redirects
the core to the `_hang` trap handler at `0xfff1010040`. The trap handler
reads `mhartid` and executes `WFI` — sleeping forever.

**Fix (in `bootrom.S`):**
```assembly
# Before (broken on rv64)
li s0, 1
slli s0, s0, 31

# After (fixed)
li s0, 1
slli s0, s0, 31
slli s0, s0, 32    ← shift upper bits out
srli s0, s0, 32    ← shift back, now 0x0000000080000000
```

**Additional fixes in the same bootrom rebuild:**
- `gen_rom.py`: `python` → `python3` (Ubuntu 24.04 has no `python` binary)
- `gen_rom.py`: Fixed `map()` usage for Python 3 (returns iterator, not list)
- `Makefile`: Updated to `-march=rv64imac_zicsr -mabi=lp64` for rv64 compilation

**Fix location:** https://github.com/radheshyam2006/cva6/tree/bootrom-fix

---

### Issue 9 — Wrong sims flag for bare ELF tests

**Symptom:** Even with correct binary, `copy_image` in `sims,2.0` copies
raw ELF as `diag.ev` and `symbol.tbl` (binary has no `.image` extension,
so the regex substitution silently produces the same path for all three
files). Monitor finds no `good_trap`/`bad_trap` symbols.

**Cause:** `-image_diag_name` is for pre-built OpenPiton image files
(`.image` + `.ev` + `.tbl` triplet). Bare ELF files from riscv-tests
should use `-asm_diag_name` with `-precompiled`.

**Fix:** Use correct sims flags:
```bash
# Wrong
sims ... -image_diag_name=rv64ui-p-add

# Correct
sims ... -precompiled -asm_diag_name=rv64ui-p-add
```

---

## CI Modernization Summary

| CI Script | Old approach | New approach |
|---|---|---|
| `ci/build-riscv-gcc.sh` | Build GCC from source (2+ hrs) | `apt install gcc-riscv64-unknown-elf picolibc-riscv64-unknown-elf` |
| `ci/install-verilator.sh` | Verilator 4.014 + Bison 3.5.1 source build | `apt install verilator` (5.020) |
| `ci/install-fesvr.sh` | Source build | Source build + `<cstdint>` patch |
| `ci/install-spike.sh` | Source build | Source build (no apt equivalent) |
| Device Tree Compiler | Source build | `apt install device-tree-compiler` |

---

## Scripts

| Script | Purpose |
|---|---|
| `clean_build.sh` | Unified build — handles all patching automatically, idempotent |
| `patch_openpiton.py` | Moves `-lstdc++` to LDFLAGS for Verilator 5.x |
| `patch_riscv_tests.py` | Patches ISA/benchmark Makefiles (zicsr, fcommon, idempotent) |
| `patch_fesvr.py` | Adds `#include <cstdint>` to fesvr headers |
| `fix_cpp.py` | Fixes const-correctness in `my_top.cpp` |