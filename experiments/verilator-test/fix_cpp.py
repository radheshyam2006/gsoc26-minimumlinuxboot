#!/usr/bin/env python3
import sys
import os

filepath = os.path.expanduser('~/openpiton/piton/tools/verilator/my_top.cpp')

if not os.path.exists(filepath):
    print(f"ERROR: File not found at {filepath}")
    sys.exit(1)

with open(filepath, 'r') as f:
    content = f.read()

old = 'extern "C" void init_jbus_model_call(char *str, int oram);'
new = 'extern "C" void init_jbus_model_call(const char *str, int oram);'

if new in content:
    print("Already fixed!")
    sys.exit(0)

if old not in content:
    print("ERROR: Could not find target line in my_top.cpp")
    sys.exit(1)

content = content.replace(old, new)

with open(filepath, 'w') as f:
    f.write(content)

print(f"Successfully patched {filepath} for const-correctness.")
