#!/bin/bash
# Script 3: Run the Stage 2 emulator with an invalid startup script path
# to test error reporting during script execution.

echo "--- Stage 2 Test 3: invalid startup script path ---"

python3 shell_emulator_stage2.py \
    --vfs-path /tmp/stage2_vfs \
    --startup-script ./no_such_script.sh

echo "--- Stage 2 Test 3 completed ---"
