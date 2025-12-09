
# commands.sh
# Example startup script for the shell emulator.

ls
cd /user/home
ls "config file.txt"

# Unknown command should be skipped
unknown_cmd --test

# Command with parser error (unclosed quote)
cd "directory with unclosed quote

exit