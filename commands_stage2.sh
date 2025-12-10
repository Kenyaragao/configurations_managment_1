# commands_stage2.sh
# Startup script to test Stage 2 configuration and command handling.

# 1. Basic ls at current directory
ls

# 2. Change directory to root (or another directory on your system)
cd /

# 3. Try ls on a path that does not exist (should print an error)
ls "/this/path/does/not/exist"

# 4. Unknown command (should be reported as 'command not found')
unknown_cmd --test

# 5. Parser error: unclosed quote (should trigger parser error and be skipped)
ls "file with unclosed quote

# 6. Exit the emulator
exit
