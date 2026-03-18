#!/usr/bin/env python3
"""Patch OpenPiton's sims script for Verilator 5.x compatibility
- Adds --no-timing flag (required by Verilator 5.x)
- Moves -lstdc++ from CFLAGS to LDFLAGS (fixes PCH generation)
"""
import sys

filepath = sys.argv[1]
with open(filepath, 'r') as f:
    content = f.read()

# Fix 1: Add --no-timing
old1 = '      $build_cmd .= "-Wno-TIMESCALEMOD " ;'
new1 = '      $build_cmd .= "-Wno-TIMESCALEMOD " ;\n      $build_cmd .= "--no-timing " ;'

# Fix 2: Move -lstdc++ from CFLAGS to LDFLAGS
old2 = '      $build_cmd .= "-CFLAGS -lstdc++ " ;'
new2 = '      $build_cmd .= "-LDFLAGS -lstdc++ " ;'

if '--no-timing' in content and '-LDFLAGS -lstdc++' in content:
    print("Already patched!")
    sys.exit(0)

if old1 not in content:
    print("ERROR: Could not find target line for --no-timing")
    sys.exit(1)

if old2 not in content:
    print("ERROR: Could not find target line for -lstdc++ fix")
    sys.exit(1)

content = content.replace(old1, new1)
content = content.replace(old2, new2)

with open(filepath, 'w') as f:
    f.write(content)

print("Patched successfully!")
print("  - Added --no-timing flag for Verilator 5.x")
print("  - Moved -lstdc++ from CFLAGS to LDFLAGS (fixes PCH generation)")
