#!/bin/bash
# Script 1: Run the emulator with a minimal VFS in interactive mode.

echo "--- Running Test 1: Minimal VFS (vfs_minimal.b64) in interactive mode ---"

python3 shell_emulator.py \
    --vfs-data-path ./vfs_minimal.b64

echo "--- Test 1 completed ---"
