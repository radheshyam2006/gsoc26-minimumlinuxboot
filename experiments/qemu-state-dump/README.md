# QEMU State Extraction Experiments

## Goal
Extract CPU state and physical memory from QEMU, analyze page tables — proving the state extraction approach works.

## Status: COMPLETED

## Scripts & Tools

### `extract_state.py` — Prototype State Extractor
- **What it does:** Connects directly to QEMU's exposed GDB server (`localhost:1234`) using the PyGDBMI wrapper. It parses GDB's output to extract all 32 integer registers, the program counter (`pc`), and missing Control and Status Registers (CSRs).
- **Why we use it:** The standard QEMU monitor (`info registers`) explicitly omits critical RISC-V CSRs like `satp` (Supervisor Address Translation and Protection). We had to build this Python script to automate GDB interaction and cleanly download the data as JSON without manual typing.

### `analyze_page_table.py` — Page Table Entry Decoder
- **What it does:** Parses a raw binary dump of physical memory. It extracts 8-byte Page Table Entries (PTEs) from the RISC-V root page table and decodes them to reveal read/write/execute permissions and pointers to sub-tables or physical pages.
- **Why we use it:** To prove that virtual memory is active. By taking the PPN (Physical Page Number) from the `satp` register and feeding it to this script, we can map out exactly where the Linux kernel resides in physical memory.

## Dependency Challenges Identified
- **Missing CSRs in QEMU:** QEMU Monitor does not dump `satp`. We were forced to depend on `gdb-multiarch` and build a pipeline connecting GDB to python to extract architectural state.
- **Sv48 vs Sv39 Translation:** We discovered QEMU uses Sv48 while the Ariane core expects Sv39. State injection scripts will need to handle this discrepancy appropriately by ensuring the correct kernel config is booted initially.

## How to Run This Experiment

### Step 1: Boot QEMU (from the qemu-boot experiment)
```bash
bash experiments/qemu-boot/setup_and_boot.sh
```

### Step 2: Dump memory (in QEMU Monitor)
Press `Ctrl+A, C` to open QEMU Monitor, then:
```
pmemsave 0x81363000 4096 /tmp/root_pt.bin
```

### Step 3: Run state extractor (in a second WSL terminal)
```bash
python3 experiments/qemu-state-dump/extract_state.py
```

### Step 4: Analyze page table (in the second WSL terminal)
```bash
python3 experiments/qemu-state-dump/analyze_page_table.py /tmp/root_pt.bin
```

## Results

Extracted JSON contains the valid `satp` register, bridging the gap left by QEMU's internal monitor. We successfully translated the root page table, identifying 58 direct physical memory mappings (Leaves) for the Linux kernel!
