# QEMU RISC-V Linux Boot Experiment

## Goal
Boot RISC-V Linux in QEMU and extract CPU/system state — proving we can capture the state needed for the MinimumLinuxBoot project.

## Status: ✅ COMPLETED

Successfully booted Ubuntu 24.04 LTS on RISC-V 64-bit in QEMU.

## Setup (Ubuntu/WSL)

```bash
# Install packages
sudo apt install qemu-system-misc opensbi u-boot-qemu cloud-image-utils gdb-multiarch

# Boot Linux (uses our setup script)
bash setup_and_boot.sh
# Login: ubuntu / gsoc2026
```

## Results

### System Info ([full output](system_info.txt))
- **Kernel:** Linux 6.17.0-14-generic riscv64
- **ISA:** rv64imafdch + many extensions
- **MMU:** sv48 (4-level page tables)
- **RAM:** 2 GB total, ~1.4 GB free
- **Hart:** 1 (single core)

### Register Dump ([full output](register_dump.txt))
Extracted via QEMU Monitor (`Ctrl+A, C` → `info registers`):

| Register | Value | Meaning |
|---|---|---|
| `pc` | `ffffffff80dce26e` | CPU executing in kernel virtual address space (S-mode) |
| `sp` (x2) | `ffffffff82403d70` | Kernel stack pointer |
| `mstatus` | `0x0a000000a0` | Machine status — S-mode context |
| `medeleg` | `0x00f0b559` | Exceptions delegated to S-mode (page faults, ecalls) |
| `mideleg` | `0x00001666` | Interrupts delegated to S-mode |
| `stvec` | `ffffffff80ddba94` | Kernel's trap handler address |
| `mtvec` | `0x800004f8` | OpenSBI's trap handler |

### Key Observations
1. **`pc` is in kernel space** (`0xffffffff...`) — confirms Linux kernel is running in supervisor mode
2. **Exception delegation** (`medeleg`) shows page faults and environment calls are delegated to S-mode — this is how Linux handles traps
3. **`satp` CSR is NOT visible** in `info registers` — need GDB stub to extract it (next experiment)
4. **`info tlb` not supported** on QEMU RISC-V — TLB state must be inferred from page tables in memory
5. **MMU mode is sv48** — OpenPiton+Ariane uses Sv39, so kernel config must be adjusted

## Next Steps
- [ ] Use GDB to extract `satp` CSR (contains page table root + MMU mode)
- [ ] Dump physical memory with `pmemsave`
- [ ] Analyze page table structure from memory dump
