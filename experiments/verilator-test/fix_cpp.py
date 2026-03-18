#!/usr/bin/env python3
"""Patch my_top.cpp for const-correctness (GCC 13+ compatibility)."""
import sys
import os

filepath = os.path.expanduser('~/openpiton/piton/tools/verilator/my_top.cpp')

if not os.path.exists(filepath):
    print(f"ERROR: File not found at {filepath}")
    sys.exit(1)

with open(filepath, 'r') as f:
    content = f.read()

modified = False

# Fix 1: Function declaration
old_decl = 'extern "C" void init_jbus_model_call(char *str, int oram);'
new_decl = 'extern "C" void init_jbus_model_call(const char *str, int oram);'

if old_decl in content:
    content = content.replace(old_decl, new_decl)
    modified = True
    print("Fixed: function declaration")

# Fix 2: Remove unnecessary cast in function call
old_call = 'init_jbus_model_call((char *) "mem.image", 0);'
new_call = 'init_jbus_model_call("mem.image", 0);'

if old_call in content:
    content = content.replace(old_call, new_call)
    modified = True
    print("Fixed: removed unnecessary cast")

if not modified:
    if new_decl in content:
        print("Already fixed!")
        sys.exit(0)
    else:
        print("ERROR: Could not find target patterns in my_top.cpp")
        sys.exit(1)

with open(filepath, 'w') as f:
    f.write(content)

print(f"Successfully patched {filepath} for const-correctness.")
