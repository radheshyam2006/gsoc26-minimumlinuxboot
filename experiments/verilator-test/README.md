# OpenPiton Verilator Build Experiment

## Goal
Build OpenPiton RTL simulation with Verilator and run a bare-metal test.

## What is a "Bare-Metal Test"?

A bare-metal test runs directly on the CPU hardware **without any OS**.  
No Linux, no bootloader — just a tiny assembly program:

```
┌──────────────┐
│  Bare Metal  │   "Hello World" assembly program
│  Test (.S)   │   runs directly on OpenPiton CPU
├──────────────┤
│  OpenPiton   │   The actual RTL hardware
│  CPU (RTL)   │   simulated in Verilator
└──────────────┘
   No OS, no boot, no kernel.
   Just: CPU turns on → runs your program → done.
```

## Setup (Ubuntu/WSL)

```bash
# 1. Install prerequisites
sudo apt install verilator build-essential python3 perl

# 2. Clone OpenPiton
git clone https://github.com/PrincetonUniversity/openpiton.git
cd openpiton

# 3. Set up environment
source piton/piton_settings.bash

# 4. Build Verilator model (single core)
sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_build

# 5. Run a hello world test  
sims -sys=manycore -x_tiles=1 -y_tiles=1 -vlt_run hello_world
```

## Results

<!-- TODO: Add build logs, test results, and any issues encountered -->
