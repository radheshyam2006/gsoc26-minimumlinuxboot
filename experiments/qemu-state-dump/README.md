# QEMU State Extraction Experiment

## Goal
Extract CPU registers, CSRs, and physical memory from a paused QEMU instance.

## Methods

### Method 1: QEMU Monitor
```bash
# Press Ctrl+A, C to open monitor
(qemu) info registers     # GPRs + PC
(qemu) info tlb           # TLB state
(qemu) pmemsave <addr> <size> <file>  # Dump memory region
```

### Method 2: GDB Remote Stub
```bash
# Start QEMU with GDB server
qemu-system-riscv64 ... -s -S

# In another terminal
gdb-multiarch
(gdb) target remote :1234
(gdb) info registers            # All GPRs
(gdb) p/x $satp                 # Read satp CSR
(gdb) p/x $mstatus              # Read mstatus CSR
(gdb) p/x $stvec                # Read stvec CSR
(gdb) x/16x 0x80000000          # Examine memory
(gdb) dump binary memory mem.bin 0x80000000 0x80001000  # Dump to file
```

### Method 3: QMP (QEMU Machine Protocol)
```bash
# Start QEMU with QMP socket
qemu-system-riscv64 ... -qmp unix:/tmp/qmp.sock,server,nowait

# Connect and query
python3 -c "
import socket, json
s = socket.socket(socket.AF_UNIX)
s.connect('/tmp/qmp.sock')
# ... send QMP commands
"
```

## Results

<!-- TODO: Add extracted register dumps, memory dumps, and analysis -->
