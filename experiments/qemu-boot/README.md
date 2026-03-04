# QEMU RISC-V Linux Boot Experiment

## Goal
Boot RISC-V Linux in QEMU and understand the boot process.

## Setup (Ubuntu/WSL)

```bash
# 1. Install QEMU
sudo apt update
sudo apt install qemu-system-misc opensbi u-boot-qemu

# 2. Download a pre-built RISC-V disk image
# Option A: Debian - https://wiki.debian.org/RISC-V
# Option B: Ubuntu - https://ubuntu.com/download/risc-v
# Option C: Minimal buildroot image

# 3. Boot Linux
qemu-system-riscv64 \
  -machine virt \
  -nographic \
  -m 2G \
  -smp 1 \
  -bios /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.bin \
  -kernel /usr/lib/u-boot/qemu-riscv64_smode/uboot.elf \
  -device virtio-net-device,netdev=eth0 \
  -netdev user,id=eth0 \
  -device virtio-rng-pci \
  -drive file=disk.img,format=raw,if=virtio
```

## What to Try After Boot

```bash
# Open QEMU Monitor: press Ctrl+A, then C
(qemu) info registers       # View all CPU registers
(qemu) info tlb             # View TLB entries  
(qemu) info mtree           # View memory map
(qemu) pmemsave 0x80000000 0x1000 mem_dump.bin  # Dump memory
```

## Results

<!-- TODO: Add screenshots and observations after running -->
