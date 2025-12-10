#!/bin/bash
# Script 2: Run the Stage 2 emulator with VFS path and a startup script.

echo "--- Stage 2 Test 2: VFS path + startup script ---"

python3 shell_emulator_stage2.py \
    --vfs-path /tmp/stage2_vfs \
    --startup-script ./commands_stage2.sh

echo "--- Stage 2 Test 2 completed ---"
