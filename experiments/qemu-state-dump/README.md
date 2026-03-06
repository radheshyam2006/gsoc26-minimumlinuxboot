# QEMU State Extraction Experiments

## Goal
Extract CPU state and physical memory from QEMU, analyze page tables — proving the state extraction approach works.

## Status: 🔄 IN PROGRESS

## Tools

### `extract_state.py` — Prototype State Extractor
Connects to QEMU via GDB and extracts all key registers + CSRs in one shot.

```bash
# 1. QEMU must be running with -s flag (from qemu-boot experiment)
# 2. In a second terminal:
python3 extract_state.py
# Output: qemu_state.json with all register values
```

### `analyze_page_table.py` — Page Table Entry Decoder
Parses a raw memory dump of a RISC-V page table and decodes each PTE.

```bash
# 1. In QEMU Monitor (Ctrl+A, C), dump the root page table:
(qemu) pmemsave 0x81363000 4096 /tmp/root_pt.bin

# 2. Analyze:
python3 analyze_page_table.py /tmp/root_pt.bin
```

## How to Run This Experiment

### Step 1: Boot QEMU (from the qemu-boot experiment)
```bash
cd /mnt/c/Users/radhe/OneDrive/Documents/gsoc/generic\ minimumlinuxboot\ for\ rtl\ simulations
bash experiments/qemu-boot/setup_and_boot.sh
# Login: ubuntu / gsoc2026
```

### Step 2: Dump memory (in QEMU Monitor)
Press `Ctrl+A, C` to open QEMU Monitor, then:
```
pmemsave 0x81363000 4096 /tmp/root_pt.bin
```
Press `Ctrl+A, C` again to return to Linux.

### Step 3: Run state extractor (in a second WSL terminal)
```bash
cd /mnt/c/Users/radhe/OneDrive/Documents/gsoc/generic\ minimumlinuxboot\ for\ rtl\ simulations
python3 experiments/qemu-state-dump/extract_state.py
```

### Step 4: Analyze page table (in the second WSL terminal)
```bash
python3 experiments/qemu-state-dump/analyze_page_table.py /tmp/root_pt.bin
```

## Results

<!-- TODO: Add output after running -->
