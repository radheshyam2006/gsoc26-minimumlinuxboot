# Research Notes

## Understanding the Project

### The Core Idea
- Hardware engineers modify OpenPiton's RTL (Verilog) and need to verify changes against a real OS (Linux)
- Booting Linux in Verilator RTL simulation takes days/weeks (billions of cycles)
- **Solution**: Boot in QEMU (minutes), save state, resume in Verilator

### What State to Save
- **CPU registers** (x0–x31, pc) — where the CPU is right now
- **CSRs** (satp, mstatus, stvec, mepc...) — MMU config, privilege level, trap vectors
- **Physical memory** (entire DRAM) — contains kernel, page tables, all data
- **Timers** (mtime, mtimecmp) — Linux scheduler depends on these
- **NOT saving**: TLB and caches — they're just caches, hardware auto-refills them from memory

### Key Insight: TLB Cold Start is Fine
- "Cold" TLB = empty = no cached address translations
- On first memory access → TLB miss → hardware walks page tables (which ARE in memory) → fills TLB
- Slow for a few microseconds, then back to normal speed
- **Zero correctness impact** — just a brief performance warmup

### Two Approaches
| | Approach A: Verilator Checkpoint | Approach B: Synthetic Assembly |
|---|---|---|
| Method | Map QEMU state to Verilator signal names | Generate RISC-V asm that programs all state |
| Speed | Instant load | Slower (must execute init instructions) |
| Robustness | Breaks if RTL changes | Works through hardware's own init path |
| Priority | Stretch goal | **Primary approach** |

## Questions for Mentors
1. Does OpenPiton+Ariane have any existing fast-forward mechanism?
2. Single-core first?
3. Approach A vs B preference?
4. Memory map alignment constraints?

## Daily Log

<!-- TODO: Add entries as you work -->
### March 5, 2026
- Created repository structure
- ...
