# commands.sh
# Comprehensive startup script to test all implemented commands and error handling.
# Intended to be used with a deep VFS that contains:
# - config.txt at the VFS root
# - level1/level2/level3/file.txt (three levels of directories)

# 1. List content of the VFS root
ls

# 2. List specific entries at the root (directory and file)
ls level1
ls config.txt

# 3. Show the content of a regular file at the root
cat config.txt

# 4. Error: try to "cat" a directory
cat level1

# 5. Error: cat a non-existing file
cat no_such_file.txt

# 6. Navigate down three levels
cd level1
ls
cd level2
ls
cd level3
ls

# 7. Read file at third level
cat file.txt

# 8. Error: cd into non-existing directory
cd no_such_dir

# 9. Error: cd into a file instead of a directory
cd file.txt

# 10. Unknown command (should be reported as an error)
unknown_cmd --test

# 11. Parser error: unclosed quote
ls "file with unclosed quote

# 12. Exit the emulator
exit
