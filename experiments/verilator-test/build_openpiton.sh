#!/bin/bash
# OpenPiton Verilator build script
set -e
cd ~/openpiton
export PITON_ROOT=~/openpiton
source piton/piton_settings.bash
export PATH=$PITON_ROOT/piton/tools/bin:$PATH

echo "=== OpenPiton Verilator Build ==="
echo "PITON_ROOT: $PITON_ROOT"
echo "Verilator: $(verilator --version)"
echo ""

# Clean previous build
rm -rf build

# Build
sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build
