#!/usr/bin/env python3
"""
extract_state.py — Extract all machine state from a paused QEMU via GDB.

This is a prototype of the state extraction tool described in the GSoC proposal.
It connects to QEMU's GDB server and extracts:
  - All 32 GPRs (x0-x31) + PC
  - Key CSRs (satp, mstatus, stvec, etc.)
  - Saves everything to a JSON file

Usage:
  1. Start QEMU with -s flag (GDB server on port 1234)
  2. Run: python3 extract_state.py
  3. Output: qemu_state.json

Requires: gdb-multiarch (installed via: sudo apt install gdb-multiarch)
"""

import subprocess
import json
import re
import sys

# Registers to extract via GDB
GPRS = [f"x{i}" for i in range(32)] + ["pc"]
CSRS = ["satp", "mstatus", "mtvec", "stvec", "mepc", "sepc", 
        "medeleg", "mideleg", "mip", "mie", "mcause", "scause",
        "mtval", "stval", "mhartid"]

def extract_register(reg_name):
    """Extract a single register value via GDB."""
    try:
        result = subprocess.run(
            ["gdb-multiarch", "-batch", "-nx",
             "-ex", "set pagination off",
             "-ex", "target remote :1234",
             "-ex", f"p/x ${reg_name}",
             "-ex", "detach",
             "-ex", "quit"],
            capture_output=True, text=True, timeout=10
        )
        # Parse output like: $1 = 0xffffffff80dce26e
        match = re.search(r'\$\d+ = (0x[0-9a-fA-F]+)', result.stdout)
        if match:
            return match.group(1)
        return None
    except Exception as e:
        return f"ERROR: {e}"

def extract_all_registers():
    """Extract all registers in one GDB session using a command file."""
    # Build GDB command script
    gdb_commands = [
        "set pagination off",
        "target remote :1234",
    ]
    
    all_regs = GPRS + CSRS
    for reg in all_regs:
        gdb_commands.append(f"printf \"REG {reg} = \"")
        gdb_commands.append(f"p/x ${reg}")
    
    gdb_commands.append("detach")
    gdb_commands.append("quit")
    
    # Write command file
    cmd_file = "/tmp/gdb_extract.txt"
    with open(cmd_file, "w") as f:
        f.write("\n".join(gdb_commands))
    
    # Run GDB with command file
    result = subprocess.run(
        ["gdb-multiarch", "-batch", "-nx", "-x", cmd_file],
        capture_output=True, text=True, timeout=30
    )
    
    # Parse results
    state = {"gprs": {}, "csrs": {}, "pc": None}
    
    for line in result.stdout.split("\n"):
        match = re.search(r'REG (\w+) = .*\$\d+ = (0x[0-9a-fA-F]+)', line)
        if not match:
            # Try alternate format
            match = re.search(r'\$\d+ = (0x[0-9a-fA-F]+)', line)
            if match and "REG" in prev_line:
                reg_match = re.search(r'REG (\w+)', prev_line)
                if reg_match:
                    reg_name = reg_match.group(1)
                    value = match.group(1)
                    if reg_name in CSRS:
                        state["csrs"][reg_name] = value
                    elif reg_name == "pc":
                        state["pc"] = value
                    else:
                        state["gprs"][reg_name] = value
        prev_line = line if "REG" in line else ""
    
    return state

def main():
    print("=" * 60)
    print("  QEMU RISC-V State Extractor (Prototype)")
    print("  GSoC 2026 — MinimumLinuxBoot")
    print("=" * 60)
    print()
    print("[*] Connecting to QEMU GDB server on :1234...")
    print("[*] Extracting key registers...")
    print()
    
    # Quick extraction of the most important registers
    key_regs = {
        "pc": None, "satp": None, "mstatus": None,
        "stvec": None, "mtvec": None, "medeleg": None,
        "mideleg": None, "sp": None, "mhartid": None
    }
    
    for reg in key_regs:
        actual_reg = "x2" if reg == "sp" else reg
        val = extract_register(actual_reg)
        key_regs[reg] = val
        if val:
            print(f"  {reg:>10} = {val}")
        else:
            print(f"  {reg:>10} = (could not read)")
    
    # Save to JSON
    output = {
        "source": "QEMU via GDB",
        "port": 1234,
        "registers": key_regs
    }
    
    output_file = "qemu_state.json"
    with open(output_file, "w") as f:
        json.dump(output, f, indent=2)
    
    print()
    print(f"[*] State saved to {output_file}")
    print()
    
    # Decode satp
    if key_regs.get("satp"):
        satp = int(key_regs["satp"], 16)
        mode = (satp >> 60) & 0xF
        asid = (satp >> 44) & 0xFFFF
        ppn = satp & 0xFFFFFFFFFFF
        pt_addr = ppn << 12
        
        mode_name = {0: "Bare", 8: "Sv39", 9: "Sv48", 10: "Sv57"}.get(mode, "Unknown")
        
        print(f"[*] satp decoded:")
        print(f"      MODE = {mode} ({mode_name})")
        print(f"      ASID = {asid}")
        print(f"      Root Page Table = 0x{pt_addr:x}")
        print()
        
        print(f"[*] To dump the root page table, run in QEMU Monitor:")
        print(f"      pmemsave 0x{pt_addr:x} 4096 /tmp/root_pt.bin")
        print(f"    Then analyze with:")
        print(f"      python3 analyze_page_table.py /tmp/root_pt.bin")

if __name__ == "__main__":
    main()
