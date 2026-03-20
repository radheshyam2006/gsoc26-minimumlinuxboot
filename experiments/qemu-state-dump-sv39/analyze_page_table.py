#!/usr/bin/env python3
"""
analyze_page_table.py — Parse RISC-V Sv48/Sv39 page table entries from a memory dump.

Usage:
  1. In QEMU Monitor (Ctrl+A, C), dump the root page table:
       pmemsave 0x81363000 4096 /tmp/root_pt.bin
  2. Run this script:
       python3 analyze_page_table.py /tmp/root_pt.bin

This reads the binary dump and decodes each 8-byte Page Table Entry (PTE).
"""

import sys
import struct

def decode_pte(pte, level_name=""):
    """Decode a single RISC-V Sv39/Sv48 PTE (8 bytes)."""
    if pte == 0:
        return None  # Empty entry
    
    valid  = (pte >> 0) & 1
    read   = (pte >> 1) & 1
    write  = (pte >> 2) & 1
    execute = (pte >> 3) & 1
    user   = (pte >> 4) & 1
    global_bit = (pte >> 5) & 1
    accessed = (pte >> 6) & 1
    dirty  = (pte >> 7) & 1
    ppn    = (pte >> 10)
    phys_addr = ppn << 12  # Physical address pointed to
    
    if not valid:
        return None
    
    # Determine type
    if read == 0 and write == 0 and execute == 0:
        pte_type = "POINTER → next level PT"
    else:
        perms = ""
        if read: perms += "R"
        if write: perms += "W"
        if execute: perms += "X"
        pte_type = f"LEAF ({perms})"
    
    flags = ""
    if user: flags += "U"
    if global_bit: flags += "G"
    if accessed: flags += "A"
    if dirty: flags += "D"
    
    return {
        "raw": pte,
        "valid": valid,
        "type": pte_type,
        "phys_addr": phys_addr,
        "flags": flags,
        "ppn": ppn
    }


def analyze_page_table(filename):
    """Read and analyze a page table dump."""
    with open(filename, "rb") as f:
        data = f.read()
    
    num_entries = len(data) // 8  # Each PTE is 8 bytes
    print(f"File: {filename}")
    print(f"Size: {len(data)} bytes ({num_entries} PTEs)")
    print(f"{'='*80}")
    print(f"{'Index':>5} | {'PTE (hex)':>18} | {'Physical Addr':>14} | {'Type':>25} | {'Flags'}")
    print(f"{'-'*80}")
    
    valid_count = 0
    pointer_count = 0
    leaf_count = 0
    
    for i in range(num_entries):
        pte_bytes = data[i*8:(i+1)*8]
        if len(pte_bytes) < 8:
            break
        pte = struct.unpack("<Q", pte_bytes)[0]  # Little-endian 64-bit
        
        result = decode_pte(pte)
        if result is None:
            continue
        
        valid_count += 1
        if "POINTER" in result["type"]:
            pointer_count += 1
        else:
            leaf_count += 1
        
        print(f"{i:>5} | 0x{result['raw']:016x} | 0x{result['phys_addr']:012x} | {result['type']:>25} | {result['flags']}")
    
    print(f"{'='*80}")
    print(f"Summary: {valid_count} valid entries ({pointer_count} pointers, {leaf_count} leaf mappings)")
    print(f"         {num_entries - valid_count} empty entries")
    

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <page_table_dump.bin>")
        print(f"  Dump with QEMU Monitor: pmemsave 0x81363000 4096 /tmp/root_pt.bin")
        sys.exit(1)
    
    analyze_page_table(sys.argv[1])
