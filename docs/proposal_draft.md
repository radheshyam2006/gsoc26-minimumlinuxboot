# GSoC 2026 Proposal: Generic MinimumLinuxBoot for RTL Simulations

**Organization:** FOSSi Foundation  
**Mentors:** Guillem López Paradís (BSC) & Jonathan Balkind (UCSB)  
**Contributor:** Radheshyam Modampuri (IIIT Hyderabad)  
**Duration:** 350 hours (Large)

---

## 1. The Problem

```mermaid
graph LR
    A["RTL Change<br/>(1 wire fix)"] --> B["Full Linux Boot<br/>in Verilator"]
    B --> C["2-7 DAYS<br/>of waiting"]
    C --> D["Test Result"]
    D -->|"Bug found"| A
    style C fill:#ff6b6b,color:#fff
```

> Hardware engineers designing OpenPiton modify RTL (Verilog) and must verify their changes against a real Linux OS. But booting Linux in cycle-accurate RTL simulation takes **days to weeks** — making iterative development impractical.

---

## 2. The Solution

```mermaid
graph LR
    A["Boot Linux<br/>in QEMU"] --> B["Save Machine<br/>State"]
    B --> C["Inject State into<br/>Verilator RTL Sim"]
    C --> D["Linux Already<br/>Running!"]
    D --> E["Run Tests"]
    
    style A fill:#4ecdc4,color:#fff
    style B fill:#45b7d1,color:#fff
    style C fill:#96ceb4,color:#fff
    style D fill:#2ecc71,color:#fff
    style E fill:#27ae60,color:#fff
```

| | Traditional | MinimumLinuxBoot |
|---|---|---|
| Boot time | Days/Weeks | **Minutes** |
| Engineering cycles | 1–2 tests/week | **Dozens/day** |
| OS-level CI testing | Impossible | **Feasible** |

---

## 3. Technical Approach

### 3.1 What State Gets Saved (and Why)

```mermaid
graph TD
    subgraph "SAVED ✅ (Essential)"
        R["CPU Registers<br/>x0-x31, pc"]
        C["CSRs<br/>satp, mstatus, stvec..."]
        M["Physical Memory<br/>(entire DRAM)"]
        T["Timers<br/>mtime, mtimecmp"]
    end
    
    subgraph "NOT SAVED ❌ (Auto-refills)"
        TLB["TLB Cache"]
        L1["L1/L2 Cache"]
    end
    
    R --> |"Where CPU resumes"| WHY["Correct<br/>Execution"]
    C --> |"MMU + privilege config"| WHY
    M --> |"All kernel data + page tables"| WHY
    
    TLB -.-> |"Hardware refills<br/>from page tables<br/>in memory"| WHY
    L1 -.-> |"Hardware refills<br/>from DRAM"| WHY
```

### 3.2 End-to-End Flow

```mermaid
flowchart TD
    A["1. QEMU boots RISC-V Linux<br/>(~3 minutes)"] --> B["2. Pause VM via<br/>QEMU Monitor / GDB"]
    B --> C["3. State Extraction Script<br/>(Python)"]
    C --> D["Extract GPRs<br/>(x0-x31, pc)"]
    C --> E["Extract CSRs<br/>(satp, mstatus,<br/>stvec, mepc...)"]
    C --> F["Dump Physical<br/>Memory (DRAM)"]
    C --> G["Read Timer/<br/>Interrupt State"]
    
    D --> H["4. Generate Synthetic<br/>Init Assembly"]
    E --> H
    F --> H
    G --> H
    
    H --> I["5. Load as 'boot<br/>firmware' in OpenPiton<br/>Verilator sim"]
    I --> J["6. Init program restores<br/>all state, jumps to<br/>saved PC"]
    J --> K["7. Linux kernel<br/>resumes execution! ✅"]
    K --> L["8. Run user-space<br/>apps (hello world, ls)"]
```

### 3.3 Two Approaches Compared

```mermaid
graph TD
    subgraph "Approach B — Synthetic Assembly (PRIMARY)"
        B1["Generate RISC-V .S file"] --> B2["Writes memory,<br/>CSRs, registers"]
        B2 --> B3["Jumps to saved PC"]
        B4["✅ Portable, debuggable"]
        B5["⚠️ Slower init (minutes)"]
    end
    
    subgraph "Approach A — Verilator Checkpoint (STRETCH)"
        A1["Map QEMU state to<br/>Verilator signal names"] --> A2["Create binary<br/>checkpoint file"]
        A2 --> A3["Load directly<br/>into sim"]
        A4["✅ Instant load"]
        A5["⚠️ Breaks if RTL changes"]
    end
```

> **Strategy:** Start with Approach B (more robust, easier to debug), explore Approach A as a stretch goal.

### 3.4 Memory Map Alignment Challenge

```mermaid
graph LR
    subgraph "QEMU virt Machine"
        Q1["0x02000000: CLINT"]
        Q2["0x0C000000: PLIC"]
        Q3["0x10000000: UART"]
        Q4["0x80000000: DRAM"]
    end
    
    subgraph "OpenPiton SoC"
        O1["0x????????: CLINT"]
        O2["0x????????: PLIC"]
        O3["0x????????: UART"]
        O4["0x????????: DRAM"]
    end
    
    Q1 -.->|"Must align"| O1
    Q2 -.->|"Must align"| O2
    Q3 -.->|"Must align"| O3
    Q4 -.->|"Must align"| O4
```

**Solution:** Compile Linux with a custom device tree matching OpenPiton's memory map, OR adjust addresses during state transfer.

---

## 4. Timeline & Milestones

```mermaid
gantt
    title Project Timeline (350 hours)
    dateFormat  YYYY-MM-DD
    
    section Phase 0
    Community Bonding           :a0, 2026-05-01, 24d
    
    section Phase 1 - Extract
    QEMU State Extraction Tool  :a1, 2026-05-25, 21d
    
    section Phase 2 - Inject
    Synthetic Init Assembly     :a2, after a1, 28d
    
    section Phase 3 - Integrate
    OpenPiton Integration       :a3, after a2, 21d
    
    section Phase 4 - Polish
    Documentation & Cleanup     :a4, after a3, 14d
```

### Detailed Breakdown

| Phase | Weeks | Deliverable | Hours |
|---|---|---|---|
| **0. Community Bonding** | 1–2 | Dev environment set up, mentor alignment on approach | — |
| **1. State Extraction** | 3–5 | `qemu_state_extractor.py` — extracts GPRs, CSRs, memory from paused QEMU | 70h |
| **2. State Injection** | 6–9 | `init_benchmark.S` — RISC-V assembly that restores full machine state in RTL | 100h |
| **3. Integration** | 10–12 | End-to-end workflow in OpenPiton infra, user-space apps running after resume | 100h |
| **4. Documentation** | 13–14 | Tutorial, cleaned-up code, upstream PR | 40h |

### Midterm Checkpoint
- ✅ QEMU state extraction working
- ✅ Synthetic init benchmark loads state into RTL
- ✅ Linux kernel prints to console after resume

### Stretch Goals
- Multi-core (multi-hart) support
- Verilator checkpoint approach (Approach A)
- Performance benchmarking framework

---

## 5. Validation Plan

```mermaid
flowchart LR
    A["Register<br/>Comparison"] --> B["Memory<br/>Checksum"]
    B --> C["Kernel<br/>Console Output"]
    C --> D["User-space<br/>App Execution"]
    
    A -.- A1["Compare QEMU regs<br/>vs RTL regs after<br/>restore"]
    B -.- B1["SHA-256 of memory<br/>before/after transfer"]
    C -.- C1["Kernel prints<br/>boot messages"]
    D -.- D1["hello world, ls,<br/>busybox commands"]
```

---

## 6. Preliminary Findings (Pre-GSoC Experiments)

I have already begun hands-on experimentation to validate the technical approach:

### Experiment 1: RISC-V Linux Boot in QEMU ✅

Successfully booted **Ubuntu 24.04 LTS** (kernel 6.17.0) on `qemu-system-riscv64 -machine virt` with OpenSBI + U-Boot.

**Boot chain observed:** OpenSBI v1.7 → U-Boot 2025.10 → Linux 6.17 → Ubuntu user-space login

### Experiment 2: CPU State Extraction via QEMU Monitor ✅

Used QEMU Monitor (`info registers`) to extract full CPU state from a running Linux system:

| Register | Extracted Value | Significance |
|---|---|---|
| `pc` | `0xffffffff80dce26e` | CPU executing in kernel virtual address space (S-mode) |
| `sp` (x2) | `0xffffffff82403d70` | Kernel stack pointer |
| `mstatus` | `0x0a000000a0` | Machine status — S-mode context, interrupts configured |
| `medeleg` | `0x00f0b559` | Page faults + ecalls delegated to S-mode (Linux handles these) |
| `mideleg` | `0x00001666` | Timer/external/software interrupts delegated to S-mode |
| `stvec` | `0xffffffff80ddba94` | Linux kernel's trap handler address |
| `mtvec` | `0x800004f8` | OpenSBI's M-mode trap handler |

### Key Discoveries

1. **`satp` CSR not available via QEMU Monitor** — requires GDB remote stub (`target remote :1234`) for extraction. This informs the tool design: the state extractor must use GDB protocol, not just the QEMU monitor.

2. **`info tlb` not supported on RISC-V in QEMU** — confirms our approach: TLB state is not extractable and not needed. Hardware page-table walks will refill TLB from the page tables already in memory.

3. **QEMU uses sv48, OpenPiton+Ariane uses Sv39** — the Linux kernel must be compiled with `CONFIG_RISCV_SV39=y` to match OpenPiton's MMU capability. This is a concrete configuration requirement identified through experimentation.

4. **Firmware base at `0x80000000`** — matches OpenPiton's expected DRAM base, which is encouraging for memory map alignment.

### Experiment 3: `satp` CSR Extraction via GDB ✅

Connected GDB to QEMU's GDB server and extracted the `satp` register:

```
satp = 0x901b600000081363
```

| Field | Value | Meaning |
|---|---|---|
| MODE (bits 63–60) | `0x9` | Sv48 — 4-level page tables |
| ASID (bits 59–44) | `0x01b6` (438) | Address Space Identifier |
| PPN (bits 43–0) | `0x00000081363` | Root page table PPN |
| **Root PT address** | **`0x81363000`** | `PPN × 4096` — physical address of root page table |

This is the single most important register for the project: it tells the MMU where the page tables live in physical memory. The synthetic init assembly would write this exact value (adjusted for Sv39) into `satp` to restore virtual memory.

> Full results: [experiments/qemu-boot/](https://github.com/radheshyam2006/gsoc26-minimumlinuxboot/tree/main/experiments/qemu-boot)

---

## 7. About Me

**Name:** Radheshyam Modampuri  
**University:** IIIT Hyderabad  
**Degree/Year:** Undergraduate, 3rd Year  
**GitHub:** [radheshyam2006](https://github.com/radheshyam2006)  
**Timezone:** IST (UTC+5:30)

### Relevant Skills
<!-- TODO: List your actual coursework and projects -->
- Computer Architecture
- Operating Systems (virtual memory, page tables)
- C/C++ programming
- RISC-V / Verilog experience (if any)

### Pre-GSoC Work
- [x] Booted RISC-V Linux in QEMU (Ubuntu 24.04, rv64, sv48)
- [x] Extracted CPU state via QEMU Monitor (registers, CSRs)
- [x] Extracted `satp` CSR via GDB — root page table at `0x81363000`
- [ ] Built OpenPiton in Verilator
- [ ] Communicated with mentors

---

## 8. Why This Project?

<!-- TODO: Write 2-3 genuine paragraphs. Some angles:
- Bridge between OS and hardware fascinates you
- Want to solve real infrastructure problems in chip design
- Interested in open-source silicon movement
- Excited by the practical impact (saving days of engineer time)
-->

---

## References

1. [RISC-V Privileged Specification](https://riscv.org/specifications/privileged-isa/)
2. [OpenPiton](https://github.com/PrincetonUniversity/openpiton)
3. [Verilator User Guide](https://verilator.org/guide/latest/)
4. [QEMU RISC-V](https://www.qemu.org/docs/master/system/riscv/virt.html)
5. [OpenSBI](https://github.com/riscv-software-src/opensbi)
6. [Pre-GSoC Experiments Repository](https://github.com/radheshyam2006/gsoc26-minimumlinuxboot)
