#!/usr/bin/env python3
import os
import socket
import shlex
import sys
import argparse

# --- Configuration ---

SUPPORTED_COMMANDS = ["ls", "cd", "exit"]


# --- Prompt / Parser ---

def generate_prompt(vfs_path: str) -> str:
    """
    Generate a shell prompt like: username@hostname:VFS_PATH$
    For Stage 2, vfs_path is just a physical path string passed by the user.
    """
    try:
        username = os.getlogin()
    except OSError:
        username = "user"

    hostname = socket.gethostname()
    # We do not really use vfs_path yet, just show it in the prompt to visualize configuration.
    return f"{username}@{hostname}:{vfs_path}$ "


def parse_command(command_line: str):
    """
    Parse a command line into a list of tokens, respecting quotes.
    If parsing fails (e.g. unclosed quote), print an error and return [].
    """
    if not command_line.strip():
        return []

    try:
        return shlex.split(command_line)
    except ValueError as e:
        print(f"shell: parser error: {e}", file=sys.stderr)
        return []


# --- Command Execution (simple real FS behaviour) ---

def execute_command(args):
    """
    Execute a single command.
    Returns True if the shell should exit, False otherwise.
    """
    if not args:
        return False

    command = args[0]
    arguments = args[1:]

    # exit
    if command == "exit":
        print("Exiting shell emulator. Goodbye!")
        return True

    # cd
    elif command == "cd":
        target = arguments[0] if arguments else os.path.expanduser("~")
        try:
            os.chdir(target)
        except FileNotFoundError:
            print(f"shell: cd: {target}: No such file or directory", file=sys.stderr)
        except NotADirectoryError:
            print(f"shell: cd: {target}: Not a directory", file=sys.stderr)
        except Exception as e:
            print(f"shell: cd: {target}: {e}", file=sys.stderr)

    # ls
    elif command == "ls":
        target = arguments[0] if arguments else "."
        try:
            entries = os.listdir(target)
            print(" ".join(sorted(entries)))
        except FileNotFoundError:
            print(f"shell: ls: {target}: No such file or directory", file=sys.stderr)
        except NotADirectoryError:
            # If target is a file, just print its name (like ls file.txt)
            print(target)
        except Exception as e:
            print(f"shell: ls: {target}: {e}", file=sys.stderr)

    # unknown command
    elif command not in SUPPORTED_COMMANDS:
        print(f"shell: **{command}**: command not found", file=sys.stderr)

    return False


# --- Startup Script Execution (requirement 2 & 3) ---

def execute_startup_script(script_path: str, vfs_path: str):
    """
    Execute commands from a startup script, line by line.
    - Empty lines and comments (#...) are skipped.
    - Erroneous lines are skipped.
    - For each line, both "input" and "output" are shown, simulating user dialogue.
    - Errors during script execution are reported.
    """
    print(f"\n--- EXECUTION STARTUP SCRIPT: {script_path} ---")

    try:
        with open(script_path, "r") as f:
            lines = f.readlines()

        for line_num, command_line in enumerate(lines, start=1):
            command_line = command_line.strip()
            if not command_line or command_line.startswith("#"):
                continue

            # Simulate user input
            print(f"Executing: {generate_prompt(vfs_path)}{command_line}")

            args = parse_command(command_line)
            if not args:
                print(
                    f"shell: ERROR in script line {line_num}: Skipping command.",
                    file=sys.stderr,
                )
                continue

            should_exit = execute_command(args)
            if should_exit:
                print("Script executed 'exit'. Terminating script execution.")
                return

    except FileNotFoundError:
        print(
            f"shell: ERROR: Startup script not found at '{script_path}'",
            file=sys.stderr,
        )
    except Exception as e:
        print(
            f"shell: An unexpected error occurred during script execution: {e}",
            file=sys.stderr,
        )

    print("--- SCRIPT EXECUTION FINISHED ---\n")


# --- REPL Loop ---

def repl_loop(vfs_path: str):
    """
    Main Read-Eval-Print Loop for interactive mode.
    """
    print("--- Starting Interactive REPL ---")
    should_exit = False

    while not should_exit:
        try:
            prompt = generate_prompt(vfs_path)
            command_line = input(prompt)
        except EOFError:
            print("\nExiting shell emulator (EOF). Goodbye!")
            break
        except KeyboardInterrupt:
            print("\n^C")
            print("Type 'exit' to quit.")
            continue

        command_line = command_line.strip()
        if not command_line:
            continue

        args = parse_command(command_line)
        if not args:
            continue

        should_exit = execute_command(args)


# --- Configuration / Entry Point (requirement 1 & debug output) ---

def configure_and_start():
    """
    Handle command-line parameters, print debug info, then run
    startup script (if any) and interactive REPL.
    """
    parser = argparse.ArgumentParser(
        description="Shell Emulator Prototype - Stage 2: Configuration"
    )

    # 1) Physical VFS path (for Stage 2 we just treat it as a configurable string)
    parser.add_argument(
        "--vfs-path",
        type=str,
        required=True,
        help="Path to the physical VFS location (for Stage 2 this is a user-defined path string).",
    )

    # 2) Startup script path
    parser.add_argument(
        "--startup-script",
        type=str,
        help="Path to a startup script file containing shell commands.",
    )

    args = parser.parse_args()

    # Debug output of all parameters
    print("--- EMULATOR STARTUP PARAMETERS ---")
    print(f"VFS Path: {args.vfs_path}")
    print(f"Startup Script: {args.startup_script if args.startup_script else 'None'}")
    print("-----------------------------------")

    # Execute startup script if provided
    if args.startup_script:
        execute_startup_script(args.startup_script, args.vfs_path)

    # Start interactive REPL
    repl_loop(args.vfs_path)


if __name__ == "__main__":
    configure_and_start()
