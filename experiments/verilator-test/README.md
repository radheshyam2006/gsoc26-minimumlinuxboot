# OpenPiton Verilator Build Attempt

## Status: ⚠️ Build started, Verilator version mismatch

## Date: March 7, 2026

## Setup
```bash
git clone --depth 1 https://github.com/PrincetonUniversity/openpiton.git ~/openpiton
cd ~/openpiton
source piton/piton_settings.bash
sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build
```

## Result
Build progressed through Verilog compilation but failed with 49 `NEEDTIMINGOPT` errors.

### Root Cause
Verilator version in Ubuntu 24.04 is too new for OpenPiton's codebase:
- OpenPiton uses Verilog `#1` timing delays (e.g., `<= #1 value`)
- Newer Verilator requires explicit `--timing` or `--no-timing` flag
- OpenPiton's build system doesn't pass this flag

### Error Example
```
%Error-NEEDTIMINGOPT: sas_intf.v:824:35: Use --timing or --no-timing 
to specify how timing controls should be handled
```

### Possible Fixes (to try with mentor guidance)
1. Add `--no-timing` to Verilator flags in OpenPiton's build config
2. Install an older Verilator version (4.x) compatible with OpenPiton
3. Check if OpenPiton's dev branch has fixed this for newer Verilator

### Key Takeaway
This is exactly the kind of build complexity documented in the proposal's
Challenges & Risks section — building OpenPiton requires specific tool
versions. This will be addressed during Community Bonding phase with
mentor guidance.
