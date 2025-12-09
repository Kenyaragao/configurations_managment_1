#!/bin/bash
# Script 2: Calls the emulator only specifying the VFS path.

echo "--- Running Test 2: VFS Path Only (Interactive Mode) ---"

# Call the Python emulator with only the VFS path
python shell_emulator.py \
    --vfs-path /my/custom/storage/area

echo "--- Test 2 Completed (Emulator is now waiting for interactive input) ---"