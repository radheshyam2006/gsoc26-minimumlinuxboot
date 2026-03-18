#!/bin/bash
# OpenPiton Verilator build script
# NOTE: Use clean_build.sh for a complete build with all patches applied
set -e

cd ~/openpiton
export PITON_ROOT=~/openpiton
export ARIANE_ROOT="$PITON_ROOT/piton/design/chip/tile/ariane"
export RISCV="/usr"  # Use system RISC-V toolchain

source piton/piton_settings.bash
export PATH=$PITON_ROOT/piton/tools/bin:$PATH

echo "=== OpenPiton Verilator Build ==="
echo "PITON_ROOT: $PITON_ROOT"
echo "Verilator: $(verilator --version)"
echo ""

# Clean previous build
rm -rf build

# Build Verilator model
sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build
