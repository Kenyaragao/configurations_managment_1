import os
import socket
import shlex
import sys

# --- Configuration and Environment ---

# Define the stub commands that the shell can recognize.
STUB_COMMANDS = {
    "ls": "ls",
    "cd": "cd",
    "exit": "exit"
}

# --- Core Functions ---

def generate_prompt():
    """
    Generates the shell prompt (e.g., username@hostname:~$).
    """
    try:
        # Get the current username
        username = os.getlogin()
    except OSError:
        # Fallback if os.getlogin() fails (e.g., in some environments)
        username = "user"
        
    # Get the hostname
    hostname = socket.gethostname()
    
    # Simple representation of the current working directory (~ for home)
    # For this minimal prototype, we'll keep the directory part simple.
    path_symbol = "~"
    
    return f"{username}@{hostname}:{path_symbol}$ "

def parse_command(command_line):
    """
    Parses the command line string into a list of arguments, correctly
    handling arguments enclosed in quotes. Uses shlex for robust parsing.
    
    Returns: A list where the first element is the command and the rest are arguments.
    """
    if not command_line:
        return []
    
    # shlex.split handles quotes and backslashes correctly
    try:
        return shlex.split(command_line)
    except ValueError as e:
        # Handle unbalanced quotes or other shlex errors
        print(f"shell: parser error: {e}")
        return []

def execute_command(args):
    """
    Executes the command based on the parsed arguments.
    Implements stub commands and error handling.
    """
    if not args:
        return False  # Continue REPL loop

    command = args[0]
    arguments = args[1:]
    
    if command == "exit":
        print("Exiting shell emulator. Goodbye!")
        return True # Signal to terminate the REPL loop
    
    elif command in STUB_COMMANDS:
        # Implements the required stub commands: ls and cd
        print(f"Stub command executed: **{command}**")
        if arguments:
            # Join the arguments for a clear display, handling quoted arguments
            print(f"Arguments provided: {arguments}")
        else:
            print("No arguments provided.")
        
    else:
        # Error handling for unknown commands
        print(f"shell: **{command}**: command not found")
        
    return False # Continue REPL loop

def repl_loop():
    """
    The main Read-Eval-Print Loop (REPL) for the shell emulator.
    """
    print("--- Shell Emulator Prototype (Stage 1) ---")
    
    should_exit = False
    while not should_exit:
        try:
            # 1. READ
            prompt = generate_prompt()
            command_line = input(prompt).strip()
            
            if not command_line:
                continue # Skip empty input
            
            # 2. EVAL (Parsing and Execution)
            args = parse_command(command_line)
            
            if args:
                should_exit = execute_command(args)
            
        except EOFError:
            # Handle Ctrl+D (End of File)
            print("\nExiting shell emulator (EOF). Goodbye!")
            should_exit = True
        except KeyboardInterrupt:
            # Handle Ctrl+C
            print("\n^C")
            print("Type 'exit' to quit.")
            continue # Continue loop after interruption
        except Exception as e:
            # General unexpected error
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            should_exit = True # Terminate on severe error

if __name__ == "__main__":
    repl_loop()