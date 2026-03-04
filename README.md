# GSoC 2026 — Generic MinimumLinuxBoot for RTL Simulations

**Organization:** [FOSSi Foundation](https://fossi-foundation.org/)  
**Mentors:** Guillem López Paradís (BSC) & Jonathan Balkind (UCSB)  
**Project Page:** [GSoC Ideas](https://fossi-foundation.org/gsoc/gsoc26-ideas#generic-minimumlinuxboot-for-rtl-simulations)

## Problem

RTL simulation of a full Linux boot on [OpenPiton](https://github.com/PrincetonUniversity/openpiton) takes days/weeks in cycle-accurate simulators like Verilator. This makes iterative hardware verification impractical.

## Solution

Boot Linux quickly in QEMU (~minutes), capture the full architectural state (CPU registers, CSRs, page tables, physical memory), and resume execution in OpenPiton's Verilator-based RTL simulation — **skipping the entire boot process**.

```
QEMU (fast boot)  ──→  Save State  ──→  Load into Verilator RTL Sim  ──→  Linux running!
    minutes              script              tool                          immediately
```

## Repository Structure

```
├── docs/                    # Proposal and research notes
│   └── proposal_draft.md    # GSoC proposal draft  
├── experiments/
│   ├── qemu-boot/           # QEMU RISC-V Linux boot experiments
│   ├── qemu-state-dump/     # State extraction experiments
│   └── verilator-test/      # OpenPiton Verilator build experiments
└── references/              # Key specs and papers
```

## Progress

- [ ] Boot RISC-V Linux in QEMU
- [ ] Extract CPU state (registers, CSRs) via GDB/QEMU Monitor
- [ ] Dump physical memory from QEMU
- [ ] Build OpenPiton with Verilator
- [ ] Run bare-metal test on OpenPiton in Verilator

## Key References

- [RISC-V Privileged Specification](https://riscv.org/specifications/privileged-isa/)
- [OpenPiton GitHub](https://github.com/PrincetonUniversity/openpiton)
- [Verilator User Guide](https://verilator.org/guide/latest/)
- [QEMU RISC-V](https://www.qemu.org/docs/master/system/riscv/virt.html)
