#!/bin/bash
# Script 1: Calls the emulator and runs the commands.sh file.

echo "--- Running Test 1: Startup Script Execution ---"

# Call the Python emulator with both parameters
python shell_emulator.py \
    --vfs-path /custom/vfs/location \
    --startup-script ./commands.sh

echo "--- Test 1 Completed ---"