import os
import socket
import shlex
import sys
import argparse

# --- Configuration and Environment ---

# Define the stub commands that the shell can recognize.
STUB_COMMANDS = {
    "ls": "ls",
    "cd": "cd",
    "exit": "exit"
}

# --- Core Functions (from Stage 1) ---

def generate_prompt():
    """Generates the shell prompt (e.g., username@hostname:~$)."""
    try:
        username = os.getlogin()
    except OSError:
        username = "user"
        
    hostname = socket.gethostname()
    path_symbol = "~"
    
    return f"{username}@{hostname}:{path_symbol}$ "

def parse_command(command_line):
    """
    Parses the command line string into a list of arguments, correctly
    handling arguments enclosed in quotes (using shlex).
    """
    if not command_line:
        return []
    
    try:
        return shlex.split(command_line)
    except ValueError as e:
        print(f"shell: parser error: {e}", file=sys.stderr)
        return []

def execute_command(args):
    """
    Executes the command based on the parsed arguments.
    Implements stub commands and error handling.
    
    Returns: True if the shell should exit, False otherwise.
    """
    if not args:
        return False

    command = args[0]
    arguments = args[1:]
    
    if command == "exit":
        return True # Signal to terminate the REPL loop
    
    elif command in STUB_COMMANDS:
        # Stub implementation
        print(f"Stub command executed: **{command}**")
        if arguments:
            print(f"Arguments provided: {arguments}")
        
    else:
        # Error handling for unknown commands
        print(f"shell: **{command}**: command not found", file=sys.stderr)
        
    return False

# --- New Functions for Stage 2: Configuration ---

def execute_startup_script(script_path):
    """
    Executes commands sequentially from a specified script file.
    Displays both input (command) and output, simulating user dialogue.
    Skips lines that cause an execution error (unknown command/parser error).
    """
    print(f"\n--- EXECUTION STARTUP SCRIPT: {script_path} ---")
    
    try:
        with open(script_path, 'r') as f:
            commands = f.readlines()
            
        for line_num, command_line in enumerate(commands):
            command_line = command_line.strip()
            
            if not command_line or command_line.startswith('#'):
                continue # Skip empty lines and comments
                
            # 1. Simulate Input/READ
            print(f"Executing: {generate_prompt()}{command_line}")
            
            # 2. EVAL (Parsing)
            args = parse_command(command_line)
            
            if not args:
                # 3. Handle Parsing Errors (skip line)
                print(f"shell: ERROR in script line {line_num + 1}: Skipping command.", file=sys.stderr)
                continue
                
            # 4. EVAL (Execution)
            should_exit = execute_command(args)
            
            if should_exit:
                print("Script executed 'exit'. Terminating script execution.")
                return # Exit the function early

    except FileNotFoundError:
        # 3. Report file error
        print(f"shell: ERROR: Startup script not found at '{script_path}'", file=sys.stderr)
        
    except Exception as e:
        # 3. Report other execution errors
        print(f"shell: An unexpected error occurred during script execution: {e}", file=sys.stderr)
        
    print(f"--- SCRIPT EXECUTION FINISHED ---\n")

def configure_and_start():
    """
    Handles command line parameters and starts the shell loop.
    """
    parser = argparse.ArgumentParser(
        description="Shell Emulator Prototype - Stage 2: Configuration."
    )
    
    # Requirement 1: VFS Path
    parser.add_argument(
        '--vfs-path', 
        type=str, 
        default='/tmp/vfs',
        help='Path to the physical location of the Virtual File System (VFS).'
    )
    
    # Requirement 1: Startup Script Path
    parser.add_argument(
        '--startup-script', 
        type=str, 
        help='Path to a script file containing shell commands to execute initially.'
    )
    
    args = parser.parse_args()
    
    # Requirement: Debug Output of all parameters
    print("--- EMULATOR STARTUP PARAMETERS ---")
    print(f"VFS Path: {args.vfs_path}")
    print(f"Startup Script: {args.startup_script if args.startup_script else 'None'}")
    print("-----------------------------------")
    
    # Execute startup script if provided
    if args.startup_script:
        execute_startup_script(args.startup_script)
        
    # Start the interactive REPL loop
    repl_loop()

def repl_loop():
    """The main Read-Eval-Print Loop (REPL) for the shell emulator."""
    print("--- Starting Interactive REPL ---")
    
    should_exit = False
    while not should_exit:
        try:
            prompt = generate_prompt()
            command_line = input(prompt).strip()
            
            if not command_line:
                continue
            
            args = parse_command(command_line)
            
            if args:
                should_exit = execute_command(args)
            
        except EOFError:
            print("\nExiting shell emulator (EOF). Goodbye!")
            should_exit = True
        except KeyboardInterrupt:
            print("\n^C")
            print("Type 'exit' to quit.")
            continue
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            should_exit = True

if __name__ == "__main__":
    configure_and_start()