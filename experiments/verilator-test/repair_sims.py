#!/usr/bin/env python3
import sys
import os

# Look for the sims script - OpenPiton often uses versions like sims,2.0
base_path = os.path.expanduser('~/openpiton/piton/tools/src/sims/')
filepath = os.path.join(base_path, 'sims,2.0')

if not os.path.exists(filepath):
    # Fallback to just 'sims' if the comma version isn't found
    filepath = os.path.join(base_path, 'sims')

if not os.path.exists(filepath):
    print(f"ERROR: Could not find sims script in {base_path}")
    sys.exit(1)

with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
changed = False

for line in lines:
    original_line = line
    # Remove --no-timing
    if '--no-timing' in line:
        line = line.replace('--no-timing', '')
        changed = True
    
    # Remove -Wno-TIMESCALEMOD
    if '-Wno-TIMESCALEMOD' in line:
        line = line.replace('-Wno-TIMESCALEMOD', '')
        changed = True
    
    # Clean up accidental double spaces from replacement
    line = line.replace('  ', ' ')
    new_lines.append(line)

if not changed:
    print("No incompatible flags found in sims script.")
else:
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    print(f"Successfully removed incompatible Verilator 5.x flags from {filepath}")
