#!/bin/bash
# GSoC MinimumLinuxBoot — QEMU RISC-V Linux Boot Setup Script
# Run this in WSL Ubuntu: bash setup_and_boot.sh

set -e

WORK_DIR=~/gsoc-qemu
IMG_FILE="$WORK_DIR/ubuntu-riscv64.img"
SEED_FILE="$WORK_DIR/seed.img"

echo "============================================"
echo " QEMU RISC-V Linux Boot Setup"
echo "============================================"

# Step 1: Install cloud-image-utils if needed
if ! command -v cloud-localds &> /dev/null; then
    echo "[*] Installing cloud-image-utils..."
    sudo apt install -y cloud-image-utils
fi

# Step 2: Create cloud-init config (sets password to 'gsoc2026')
echo "[*] Creating cloud-init configuration..."
cat > "$WORK_DIR/user-data" << 'EOF'
#cloud-config
password: gsoc2026
chpasswd: { expire: False }
ssh_pwauth: True
EOF

# Step 3: Create seed ISO for cloud-init
echo "[*] Creating seed ISO..."
cloud-localds "$SEED_FILE" "$WORK_DIR/user-data"

# Step 4: Resize image to 10 GB (cloud image is only 4.5 GB)
echo "[*] Resizing disk image to 10 GB..."
qemu-img resize "$IMG_FILE" 10G 2>/dev/null || true

echo ""
echo "============================================"
echo " Setup complete! Now booting..."
echo " Login credentials:"
echo "   Username: ubuntu"
echo "   Password: gsoc2026"
echo ""
echo " QEMU Controls:"
echo "   Ctrl+A, C  →  Open QEMU Monitor (type 'info registers')"
echo "   Ctrl+A, C  →  Switch back to guest console"
echo "   Ctrl+A, X  →  Kill QEMU"
echo "============================================"
echo ""
echo "[*] Booting RISC-V Linux... (this takes 2-3 minutes)"
echo ""

# Step 5: Boot!
qemu-system-riscv64 \
    -machine virt \
    -nographic \
    -m 2G \
    -smp 1 \
    -bios /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.bin \
    -kernel /usr/lib/u-boot/qemu-riscv64_smode/uboot.elf \
    -device virtio-blk-device,drive=hd0 \
    -drive file="$IMG_FILE",format=qcow2,id=hd0 \
    -device virtio-blk-device,drive=cloud \
    -drive if=none,id=cloud,file="$SEED_FILE",format=raw \
    -device virtio-net-device,netdev=eth0 \
    -netdev user,id=eth0
