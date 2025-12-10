#!/bin/bash
# Script 1: Run the Stage 2 emulator with only the VFS path (interactive mode).

echo "--- Stage 2 Test 1: VFS path only (interactive mode) ---"

python3 shell_emulator_stage2.py \
    --vfs-path /tmp/stage2_vfs

echo "--- Stage 2 Test 1 completed ---"
