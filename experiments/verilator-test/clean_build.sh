#!/bin/bash
# Clean OpenPiton + Ariane Build Script for Modern Systems
# Tested with: Ubuntu 24.04, GCC 13+, Verilator 5.x
#
# This script handles all patching and compatibility issues for building
# OpenPiton with Verilator on modern Linux distributions.

set -e
set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

#------------------------------------------------------------------------------
# Configuration
#------------------------------------------------------------------------------
OPENPITON_ROOT="${OPENPITON_ROOT:-$HOME/openpiton}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NUM_JOBS="${NUM_JOBS:-$(nproc)}"

# RISCV prefix for spike/fesvr installation (must be writable)
RISCV_LOCAL="$OPENPITON_ROOT/piton/design/chip/tile/ariane/tmp"

#------------------------------------------------------------------------------
# Verify Prerequisites
#------------------------------------------------------------------------------
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing=()

    # Check required commands
    for cmd in verilator gcc riscv64-unknown-elf-gcc git python3; do
        if ! command -v "$cmd" &>/dev/null; then
            missing+=("$cmd")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Missing required tools: ${missing[*]}"
        echo ""
        echo "Install with:"
        echo "  sudo apt install gcc g++ verilator gcc-riscv64-unknown-elf picolibc-riscv64-unknown-elf git python3"
        exit 1
    fi

    # Show versions
    log_info "Tool versions:"
    echo "  Verilator: $(verilator --version 2>&1 | head -1)"
    echo "  GCC: $(gcc --version 2>&1 | head -1)"
    echo "  RISC-V GCC: $(riscv64-unknown-elf-gcc --version 2>&1 | head -1)"

    # Check OpenPiton exists
    if [[ ! -d "$OPENPITON_ROOT" ]]; then
        log_error "OpenPiton not found at $OPENPITON_ROOT"
        echo "Clone it with: git clone https://github.com/PrincetonUniversity/openpiton.git $OPENPITON_ROOT"
        exit 1
    fi

    log_info "Prerequisites OK"
}

#------------------------------------------------------------------------------
# Setup Environment
#------------------------------------------------------------------------------
setup_environment() {
    log_info "Setting up environment..."

    export PITON_ROOT="$OPENPITON_ROOT"
    export ARIANE_ROOT="$PITON_ROOT/piton/design/chip/tile/ariane"

    # RISCV is used by install-spike.sh and install-fesvr.sh for installation prefix
    # Must be a writable directory
    export RISCV="$RISCV_LOCAL"

    # Add local RISCV bin to PATH (for spike, fesvr)
    export PATH="$RISCV/bin:$PATH"

    cd "$PITON_ROOT"

    # Source OpenPiton settings
    if [[ -f piton/piton_settings.bash ]]; then
        source piton/piton_settings.bash
    else
        log_error "piton_settings.bash not found"
        exit 1
    fi

    export PATH="$PITON_ROOT/piton/tools/bin:$PATH"

    log_info "Environment setup complete"
    log_info "  PITON_ROOT: $PITON_ROOT"
    log_info "  RISCV (for spike/fesvr): $RISCV"
}

#------------------------------------------------------------------------------
# Patch sims script for Verilator 5.x
#------------------------------------------------------------------------------
patch_sims_for_verilator5() {
    log_info "Checking sims script for Verilator 5.x compatibility..."

    local sims_file="$PITON_ROOT/piton/tools/src/sims/sims,2.0"

    if [[ ! -f "$sims_file" ]]; then
        log_error "sims script not found at $sims_file"
        exit 1
    fi

    # Check if already patched
    if grep -q -- '--no-timing' "$sims_file" && grep -q -- '-LDFLAGS -lstdc++' "$sims_file"; then
        log_info "sims script already patched for Verilator 5.x"
        return 0
    fi

    log_info "Patching sims script for Verilator 5.x..."
    python3 "$SCRIPT_DIR/patch_openpiton.py" "$sims_file"
}

#------------------------------------------------------------------------------
# Patch my_top.cpp for const-correctness
#------------------------------------------------------------------------------
patch_my_top_cpp() {
    log_info "Checking my_top.cpp for const-correctness..."

    local cpp_file="$PITON_ROOT/piton/tools/verilator/my_top.cpp"

    if [[ ! -f "$cpp_file" ]]; then
        log_warn "my_top.cpp not found (will be created during build)"
        return 0
    fi

    if grep -q 'const char \*str' "$cpp_file"; then
        log_info "my_top.cpp already patched"
        return 0
    fi

    log_info "Patching my_top.cpp..."
    python3 "$SCRIPT_DIR/fix_cpp.py"
}

#------------------------------------------------------------------------------
# Build RISC-V tests and tools
#------------------------------------------------------------------------------
build_riscv_tools() {
    log_info "Building RISC-V tests and tools..."

    cd "$PITON_ROOT"

    # Initialize submodules
    log_info "Initializing Ariane submodule..."
    git submodule update --init --recursive piton/design/chip/tile/ariane 2>/dev/null || true

    cd piton/design/chip/tile/ariane/

    # Create tmp directory
    ci/make-tmp.sh 2>/dev/null || true

    # Install FESVR and Spike
    # These scripts share the same riscv-isa-sim repo, so handle together
    if [[ ! -f "$RISCV/lib/libfesvr.a" ]] || [[ ! -f "$RISCV/bin/spike" ]]; then
        # Clone riscv-isa-sim if needed
        if [[ ! -d tmp/riscv-isa-sim ]]; then
            log_info "Cloning riscv-isa-sim..."
            cd tmp
            git clone https://github.com/riscv/riscv-isa-sim.git
            cd riscv-isa-sim
            git checkout 35d50bc40e59ea1d5566fbd3d9226023821b1bb6
            cd ../..
        fi

        # Patch fesvr for GCC 13+ BEFORE building
        log_info "Patching FESVR for modern GCC..."
        python3 "$SCRIPT_DIR/patch_fesvr.py"

        # Build and install fesvr
        if [[ ! -f "$RISCV/lib/libfesvr.a" ]]; then
            log_info "Building FESVR..."
            cd tmp/riscv-isa-sim
            rm -rf build
            mkdir -p build
            cd build
            ../configure --prefix="$RISCV/"
            make install-config-hdrs install-hdrs libfesvr.a -j"$NUM_JOBS"
            mkdir -p "$RISCV/lib"
            cp libfesvr.a "$RISCV/lib/"
            cd ../../..
        fi

        # Build and install spike
        if [[ ! -f "$RISCV/bin/spike" ]]; then
            log_info "Building Spike..."
            cd tmp/riscv-isa-sim/build
            make -j"$NUM_JOBS"
            make install
            cd ../../..
        fi
    else
        log_info "FESVR and Spike already installed"
    fi

    # Build RISC-V tests
    build_riscv_tests

    cd "$PITON_ROOT"
}

#------------------------------------------------------------------------------
# Build RISC-V tests
#------------------------------------------------------------------------------
build_riscv_tests() {
    log_info "Building RISC-V tests..."

    local VERSION="7cc76ea83b4f827596158c8ba0763e93da65de8f"

    cd tmp

    # Clone tests if needed
    if [[ ! -d riscv-tests ]]; then
        log_info "Cloning riscv-tests..."
        git clone https://github.com/riscv/riscv-tests.git
    fi

    cd riscv-tests
    git checkout "$VERSION" 2>/dev/null || true
    git submodule update --init --recursive 2>/dev/null || true

    # Apply patches using our idempotent script
    log_info "Patching RISC-V tests for modern GCC..."
    python3 "$SCRIPT_DIR/patch_riscv_tests.py"

    # Setup syscalls symlinks
    cd benchmarks/common/
    rm -f syscalls.c util.h
    ln -sf "${PITON_ROOT}/piton/verif/diag/assembly/include/riscv/ariane/syscalls.c"
    ln -sf "${PITON_ROOT}/piton/verif/diag/assembly/include/riscv/ariane/util.h"
    cd - >/dev/null

    # Configure and build
    autoconf 2>/dev/null || true
    mkdir -p build
    cd build

    log_info "Configuring RISC-V tests..."
    ../configure --prefix="$ARIANE_ROOT/tmp/riscv-tests/build"

    log_info "Building ISA tests..."
    make clean 2>/dev/null || true
    make isa -j"$NUM_JOBS" 2>&1 | tail -5

    log_info "Building benchmarks..."
    make benchmarks -j"$NUM_JOBS" 2>&1 | tail -5

    make install

    cd "$ARIANE_ROOT"
}

#------------------------------------------------------------------------------
# Build Verilator model
#------------------------------------------------------------------------------
build_verilator_model() {
    log_info "Building Verilator model..."

    cd "$PITON_ROOT"

    # Clean previous build
    rm -rf build

    log_info "Starting Verilator build (this may take a while)..."
    log_info "Command: sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build"

    sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build 2>&1 | tee build.log | tail -50

    # Check if build succeeded
    if [[ -f build/manycore/rel-0.1/obj_dir/Vcmp_top ]]; then
        log_info "Build SUCCESSFUL!"
        log_info "Executable: build/manycore/rel-0.1/obj_dir/Vcmp_top"
    else
        log_error "Build failed. Check build.log for details."
        exit 1
    fi
}

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------
main() {
    echo "=============================================="
    echo "OpenPiton Verilator Build Script"
    echo "=============================================="
    echo ""

    check_prerequisites
    setup_environment
    patch_sims_for_verilator5
    patch_my_top_cpp

    # Check what action to perform
    case "${1:-all}" in
        tools)
            build_riscv_tools
            ;;
        verilator)
            build_verilator_model
            ;;
        all)
            build_riscv_tools
            build_verilator_model
            ;;
        *)
            echo "Usage: $0 [tools|verilator|all]"
            echo "  tools     - Build RISC-V tests and tools only"
            echo "  verilator - Build Verilator model only"
            echo "  all       - Build everything (default)"
            exit 1
            ;;
    esac

    echo ""
    log_info "Build complete!"
}

main "$@"
