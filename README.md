# GSoC 2026 — Generic MinimumLinuxBoot for RTL Simulations

**Contributor:** Radheshyam Modampuri (IIIT Hyderabad)  
**Organization:** [FOSSi Foundation](https://fossi-foundation.org/)  
**Mentors:** Guillem López Paradís (BSC) & Jonathan Balkind (UCSB)  
**Project Page:** [GSoC Ideas](https://fossi-foundation.org/gsoc/gsoc26-ideas#generic-minimumlinuxboot-for-rtl-simulations)

## Problem

RTL simulation of a full Linux boot on [OpenPiton](https://github.com/PrincetonUniversity/openpiton) takes **days/weeks** in cycle-accurate simulators like Verilator. This makes iterative hardware verification impractical.

## Solution

Boot Linux quickly in QEMU (~minutes), capture the full architectural state (CPU registers, CSRs, page tables, physical memory), and resume execution in OpenPiton's Verilator-based RTL simulation — **skipping the entire boot process**.

```
QEMU (fast boot)  ──→  Save State  ──→  Load into Verilator RTL Sim  ──→  Linux running!
    minutes              script              tool                          immediately
```

## Repository Structure

```
├── docs/
│   ├── proposal_draft.md    ← GSoC proposal (main document)
│   └── research_notes.md    ← Research notes & daily log
├── experiments/
│   ├── qemu-boot/           ← RISC-V Linux boot (COMPLETED)
│   │   ├── register_dump.txt    ← CPU register dump with analysis
│   │   ├── system_info.txt      ← cpuinfo, meminfo, uname
│   │   └── setup_and_boot.sh   ← Reproducible boot script
│   ├── qemu-state-dump/     ← State extraction via GDB (next)
│   └── verilator-test/      ← OpenPiton Verilator build (planned)
└── references/
    └── key_references.md    ← Specs, docs, YouTube resources
```

## Current Status

- Booted RISC-V Linux in QEMU (rootfs via BusyBox).
- Extracted architectural state (Registers, CSRs) using QEMU Monitor and GDB.
- Successfully decoded root page table entries (PTEs) for Sv48/Sv39.
- Documented key findings (Sv48 vs Sv39, satp extraction needs GDB).
- Extracted satp CSR via GDB — root page table at 0x81363000.
- Dumped physical memory from QEMU and analyzed page tables.
- Built OpenPiton with Verilator.
- Run bare-metal test on OpenPiton.

## Key Findings So Far

| Finding | Implication |
|---|---|
| `pc = 0xffffffff80dce26e` | Kernel runs in virtual address space — MMU is active |
| `medeleg = 0x00f0b559` | Page faults delegated to S-mode — Linux handles VM |
| QEMU uses sv48, OpenPiton uses Sv39 | Must compile kernel with `CONFIG_RISCV_SV39=y` |
| `satp` not in QEMU monitor | State extractor must use GDB protocol |
| Firmware base `0x80000000` | Matches OpenPiton's DRAM base  |

## Key References

- [RISC-V Privileged Specification](https://riscv.org/specifications/privileged-isa/)
- [OpenPiton GitHub](https://github.com/PrincetonUniversity/openpiton)
- [Verilator User Guide](https://verilator.org/guide/latest/)
- [QEMU RISC-V](https://www.qemu.org/docs/master/system/riscv/virt.html)
