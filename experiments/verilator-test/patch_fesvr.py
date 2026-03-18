import os

def patch_fesvr():
    device_h_path = os.path.expanduser("~/openpiton/piton/design/chip/tile/ariane/tmp/riscv-isa-sim/fesvr/device.h")
    
    if not os.path.exists(device_h_path):
        print(f"File not found: {device_h_path}")
        return

    with open(device_h_path, "r") as f:
        content = f.read()

    # If <cstdint> is already included, we don't need to patch it again
    if "<cstdint>" in content:
        print("fesvr/device.h is already patched.")
        return

    # Modern GCC (13+) requires explicit inclusion of <cstdint> for uint64_t
    parts = content.split('#include <functional>\n', 1)
    if len(parts) == 2:
        new_content = parts[0] + '#include <functional>\n#include <cstdint>\n' + parts[1]
        with open(device_h_path, "w") as f:
            f.write(new_content)
        print("Successfully patched fesvr/device.h to include <cstdint>")
    else:
        print("Could not find the expected insertion point in fesvr/device.h")

if __name__ == "__main__":
    patch_fesvr()
