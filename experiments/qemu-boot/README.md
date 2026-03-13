# QEMU RISC-V Linux Boot Experiment

## Goal
Boot RISC-V Linux in QEMU and extract CPU/system state — proving we can capture the state needed for the MinimumLinuxBoot project.

## Status: COMPLETED

Successfully booted Ubuntu 24.04 LTS on RISC-V 64-bit in QEMU.

## Scripts & Tools

### `setup_and_boot.sh`
This bash script automates the downloading and booting of a pre-built RISC-V Ubuntu Cloud Image. 
- **What it does:** It downloads the Ubuntu image, resizes it, creates a `cloud-init` configuration (to set the default username/password), and launches `qemu-system-riscv64` with the necessary flags for a `virt` machine.
- **Why we use it:** Instead of manually configuring QEMU disks and networks every time, this script ensures we boot the exact same environment consistently in 1-3 minutes. It exposes a GDB server on port 1234 (`-s`) for the next phase.

## Dependencies Encountered
- `qemu-system-misc`: Provides `qemu-system-riscv64`.
- `cloud-image-utils`: Provides `cloud-localds` to build the config drive for the Ubuntu image.
- `gdb-multiarch`: Required for connecting to the GDB stub later.

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
1. **`pc` is in kernel space** (`0xffffffff...`) — confirms Linux kernel is running in supervisor mode.
2. **`satp` CSR is MISSING** in QEMU `info registers`. QEMU's monitor does not expose all RISC-V CSRs, which created a hard dependency on using GDB.
3. **MMU mode is sv48** — OpenPiton+Ariane uses Sv39, indicating that our final target Linux kernel must be compiled with `CONFIG_RISCV_SV39=y`.

## Next Steps
- Use GDB to extract the missing `satp` CSR.
- Extract physical memory.
