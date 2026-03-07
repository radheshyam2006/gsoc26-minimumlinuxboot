#!/usr/bin/env python3
"""Patch OpenPiton's sims script to add --no-timing for Verilator 5.x"""
import sys

filepath = sys.argv[1]
with open(filepath, 'r') as f:
    content = f.read()

old = '      $build_cmd .= "-Wno-TIMESCALEMOD " ;'
new = '      $build_cmd .= "-Wno-TIMESCALEMOD " ;\n      $build_cmd .= "--no-timing " ;'

if '--no-timing' in content:
    print("Already patched!")
    sys.exit(0)

if old not in content:
    print("ERROR: Could not find target line")
    sys.exit(1)

content = content.replace(old, new)

with open(filepath, 'w') as f:
    f.write(content)

print("Patched successfully! Added --no-timing flag.")
