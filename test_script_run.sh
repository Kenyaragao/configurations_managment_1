#!/bin/bash
# Script 1: Run the emulator with a deep VFS and the commands.sh startup script.

echo "--- Running Test 1: Deep VFS with startup script (commands.sh) ---"

# Call the Python emulator with both parameters
python3 shell_emulator.py \
    --vfs-data-path ./vfs_deep.b64 \
    --startup-script ./commands.sh

echo "--- Test 1 completed ---"
