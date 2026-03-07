# OpenPiton Verilator Build Attempt

## Status: ⚠️ RTL compilation succeeds, C++ linking fails (Verilator version mismatch)

## Date: March 7, 2026

## Environment
- **OS:** Ubuntu 24.04 on WSL2
- **Verilator:** 5.020 (2024-01-01)
- **GCC:** 13.2.0

## Setup
```bash
git clone --depth 1 https://github.com/PrincetonUniversity/openpiton.git ~/openpiton
export PITON_ROOT=$HOME/openpiton
source $PITON_ROOT/piton/piton_settings.bash
$PITON_ROOT/piton/tools/bin/sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build
```

## Build Progress

### Issue 1: `cc1` not found ✅ FIXED
```
bw_cpp: fatal error: cannot execute 'cc1'
```
**Fix:** `sudo ln -s /usr/libexec/gcc/x86_64-linux-gnu/13/cc1 /usr/bin/cc1`

### Issue 2: `NEEDTIMINGOPT` errors ✅ FIXED
Verilator 5.x requires explicit `--timing` or `--no-timing` flag.
OpenPiton's Verilog uses `#1` timing delays.
```
%Error-NEEDTIMINGOPT: Use --timing or --no-timing
```
**Fix:** Patched `sims,2.0` to add `--no-timing` flag (see `patch_openpiton.py`)

### Issue 3: C++ linking fails ❌ UNRESOLVED
After Verilator successfully compiles all RTL to C++, the `make` step fails:
```
undefined reference to `main'
make: *** [Vcmp_top__pch.h.fast.gch] Error 1
```
This is a Verilator 5.x precompiled header (PCH) issue — OpenPiton's build
system wasn't designed for Verilator 5.x's PCH generation.

### Possible fixes (needs mentor guidance)
1. Use Verilator 4.x (what OpenPiton was tested with)
2. Disable PCH in Verilator 5.x build
3. Check OpenPiton's CI/CD for recommended Verilator version

## Tools Created
- `patch_openpiton.py` — Patches sims,2.0 to add --no-timing flag
- `build_openpiton.sh` — Build script with proper environment setup

## Key Takeaway
Building OpenPiton requires specific tool versions aligned with their CI.
This will be resolved during Community Bonding with mentor guidance on
the recommended development environment.
