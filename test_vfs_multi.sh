#!/bin/bash
# Script 3: Run the emulator with a VFS that has multiple files and directories.

echo "--- Running Test 3: Multi-file VFS (vfs_multi.b64) with simple test script ---"

python3 shell_emulator.py \
    --vfs-data-path ./vfs_multi.b64 \
    --startup-script ./vfs_test_commands.sh

echo "--- Test 3 completed ---"
