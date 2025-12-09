import os
import socket
import shlex
import sys
import argparse
import zipfile
import io
import base64

# --- Parser (Stage 1/2 compatibility) ---

def parse_command(command_line):
    """
    Parse a command line into a list of arguments, respecting quotes.
    """
    if not command_line:
        return []
    try:
        return shlex.split(command_line)
    except ValueError as e:
        print(f"shell: parser error: {e}", file=sys.stderr)
        return []

# --- Configuration and Environment ---

SUPPORTED_COMMANDS = ["ls", "cd", "exit", "cat"]


# Define the stub commands (now updated for VFS operations)
SUPPORTED_COMMANDS = ["ls", "cd", "exit", "cat"] # Adding 'cat' for viewing VFS files

# --- VFS Core Implementation ---

class VirtualFileSystem:
    """Handles VFS operations in memory, loaded from a base64-encoded ZIP archive."""
    
    def __init__(self, zip_data_b64):
        self.current_path = "/"
        self.vfs_content = {}  # Stores file/directory structure and content
        self.load_from_base64(zip_data_b64)

    def load_from_base64(self, zip_data_b64):
        """
        Loads the VFS structure and content from a base64-encoded ZIP file.
        Requirement 1: All operations in memory.
        Requirement 2: Source is ZIP, binary data is base64.
        """
        try:
            # 1. Decode Base64 data
            zip_data = base64.b64decode(zip_data_b64)
            zip_buffer = io.BytesIO(zip_data)
            
            # 2. Open ZIP archive in memory
            with zipfile.ZipFile(zip_buffer, 'r') as zf:
                
                # Check for structure consistency
                if not zf.namelist():
                    raise ValueError("ZIP archive is empty.")
                    
                for member in zf.infolist():
                    path = '/' + member.filename.rstrip('/') # Standardize path, remove trailing slash

                    if member.is_dir():
                        self.vfs_content[path] = {'type': 'dir', 'content': None}
                    else:
                        # File: store content and mark as file
                        with zf.open(member.filename) as file:
                            # Read content and store it directly in memory
                            file_content = file.read().decode('utf-8', errors='ignore')
                            self.vfs_content[path] = {'type': 'file', 'content': file_content}
            
            print(f"VFS: Successfully loaded {len(self.vfs_content)} entries from archive.")
            
        except zipfile.BadZipFile:
            raise ValueError("VFS load error: Invalid or corrupted ZIP file format.")
        except Exception as e:
            # Requirement 3: Report VFS loading error
            raise RuntimeError(f"VFS load error: Failed to process VFS data ({e})")

    def _get_path_parts(self, path):
        """Converts VFS path (e.g., /a/b/c) into a list of components."""
        return [p for p in path.split('/') if p]

    def _normalize_path(self, path):
        """Converts a relative path to an absolute VFS path."""
        if path.startswith('/'):
            return path.rstrip('/') if path != '/' else '/'
            
        # Handle relative path
        parts = self._get_path_parts(self.current_path)
        
        for part in self._get_path_parts(path):
            if part == '..':
                if len(parts) > 0:
                    parts.pop()
            elif part != '.':
                parts.append(part)
                
        return '/' + '/'.join(parts)
        
    def cd(self, target_path):
        """Requirement 1: Change current_path within VFS."""
        new_path = self._normalize_path(target_path)
        
        if new_path == '': # Handle cd to root from relative path
            new_path = '/'
            
        # Check if the path exists and is a directory
        if new_path not in self.vfs_content and new_path != '/':
            return False, f"cd: {target_path}: No such file or directory"
        
        if new_path != '/' and self.vfs_content.get(new_path, {}).get('type') != 'dir':
            return False, f"cd: {target_path}: Not a directory"

        self.current_path = new_path
        return True, None

    def ls(self, path="."):
        """Requirement 3: List content of the current or specified path."""
        target = self._normalize_path(path)
        
        if target == '/':
            parent_parts = []
        else:
            parent_parts = self._get_path_parts(target)
            
        if target not in self.vfs_content and target != '/':
            return False, f"ls: {path}: No such file or directory"
            
        if target != '/' and self.vfs_content.get(target, {}).get('type') != 'dir':
             return True, target.split('/')[-1] # ls on a file returns the filename itself

        # List contents
        contents = []
        prefix = target if target == '/' else target + '/'
        
        for entry_path in self.vfs_content:
            if entry_path.startswith(prefix) and entry_path != prefix:
                # Get the name of the file/dir immediately under the target
                remainder = entry_path[len(prefix):]
                name = remainder.split('/')[0]
                
                if name not in contents:
                    contents.append(name)
                    
        return True, ' '.join(sorted(contents))

    def cat(self, path):
        """New command to display the content of a VFS file."""
        target = self._normalize_path(path)
        
        if target not in self.vfs_content:
            return False, f"cat: {path}: No such file or directory"
            
        entry = self.vfs_content[target]
        
        if entry.get('type') == 'dir':
            return False, f"cat: {path}: Is a directory"
            
        return True, entry.get('content', '')


# --- Core Functions (Updated for VFS) ---

VFS_INSTANCE = None # Global instance to be initialized at startup

def generate_prompt(vfs_path):
    """Generates the shell prompt (e.g., username@hostname:VFS_PATH$)."""
    try:
        username = os.getlogin()
    except OSError:
        username = "user"
        
    hostname = socket.gethostname()
    
    # Use VFS current path for prompt
    path_symbol = vfs_path if vfs_path != '/' else ''
    
    return f"{username}@{hostname}:{path_symbol}{VFS_INSTANCE.current_path}$ "

def execute_command(args):
    """Executes the command, now including VFS operations."""
    if not args:
        return False

    command = args[0]
    arguments = args[1:]
    
    if command == "exit":
        print("Exiting shell emulator. Goodbye!")
        return True
    
    # --- VFS COMMANDS ---
    elif command == "cd":
        target = arguments[0] if arguments else "/"
        success, message = VFS_INSTANCE.cd(target)
        if not success:
            print(f"shell: {message}", file=sys.stderr)
            
    elif command == "ls":
        target = arguments[0] if arguments else "."
        success, output = VFS_INSTANCE.ls(target)
        if success:
            print(output)
        else:
            print(f"shell: {output}", file=sys.stderr)
            
    elif command == "cat":
        if not arguments:
            print("shell: cat: Missing file operand", file=sys.stderr)
            return False
            
        target = arguments[0]
        success, output = VFS_INSTANCE.cat(target)
        if success:
            print(output)
        else:
            print(f"shell: {output}", file=sys.stderr)
            
    # --- UNKNOWN COMMANDS ---
    elif command not in SUPPORTED_COMMANDS:
        print(f"shell: **{command}**: command not found", file=sys.stderr)
        
    # --- Commands from Stage 1/2 (if they had logic) ---
    # Since only cd/ls were stubs, they are now real VFS implementations.
        
    return False

# ... (parse_command, execute_startup_script, repl_loop functions remain the same as Stage 2,
#      except for the prompt generation call in repl_loop which now passes VFS path) ...

def repl_loop(vfs_path):
    """The main Read-Eval-Print Loop (REPL) for the shell emulator."""
    print("--- Starting Interactive REPL ---")
    
    should_exit = False
    while not should_exit:
        try:
            # NOTE: Prompt generation now uses the VFS path
            prompt = generate_prompt(vfs_path)
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

def execute_startup_script(script_path, vfs_path):
    # ... (same as Stage 2, but prompt call uses vfs_path) ...
    # Update: Pass vfs_path to repl_loop call as well if the script ends without 'exit'
    
    # (Leaving this implementation concise for space, assuming previous functions are adapted)
    
    print(f"\n--- EXECUTION STARTUP SCRIPT: {script_path} ---")
    
    try:
        with open(script_path, 'r') as f:
            commands = f.readlines()
            
        for line_num, command_line in enumerate(commands):
            # ... (same logic as before) ...
            command_line = command_line.strip()
            if not command_line or command_line.startswith('#'): continue

            # Simulate Input/READ (Updated to use VFS prompt)
            print(f"Executing: {generate_prompt(vfs_path)}{command_line}")
            
            args = parse_command(command_line)
            
            if not args:
                print(f"shell: ERROR in script line {line_num + 1}: Skipping command.", file=sys.stderr)
                continue
                
            should_exit = execute_command(args)
            
            if should_exit:
                print("Script executed 'exit'. Terminating script execution.")
                return # Exit the function early

    except FileNotFoundError:
        print(f"shell: ERROR: Startup script not found at '{script_path}'", file=sys.stderr)
    except Exception as e:
        print(f"shell: An unexpected error occurred during script execution: {e}", file=sys.stderr)
        
    print(f"--- SCRIPT EXECUTION FINISHED ---\n")


def configure_and_start():
    """Handles command line parameters, loads VFS, and starts the shell loop."""
    global VFS_INSTANCE # We need to assign the global instance here
    
    parser = argparse.ArgumentParser(
        description="Shell Emulator Prototype - Stage 3: VFS."
    )
    
    # VFS data path (Note: This is now the path to the base64-encoded ZIP file)
    parser.add_argument(
        '--vfs-data-path', 
        type=str, 
        required=True, # VFS is now mandatory
        help='Path to the base64-encoded ZIP file containing the VFS data.'
    )
    
    # Startup Script Path
    parser.add_argument(
        '--startup-script', 
        type=str, 
        help='Path to a script file containing shell commands to execute initially.'
    )
    
    args = parser.parse_args()
    
    print("--- EMULATOR STARTUP PARAMETERS ---")
    print(f"VFS Data Path: {args.vfs_data_path}")
    print(f"Startup Script: {args.startup_script if args.startup_script else 'None'}")
    print("-----------------------------------")
    
    try:
        # 1. Load VFS content from file
        with open(args.vfs_data_path, 'r') as f:
            zip_data_b64 = f.read().strip()
            
        # 2. Initialize VFS Instance
        VFS_INSTANCE = VirtualFileSystem(zip_data_b64)
        
    except FileNotFoundError:
        # Requirement 3: Report file not found error
        print(f"shell: VFS load error: File not found at '{args.vfs_data_path}'", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        # Requirement 3: Report format error (corrupted ZIP/Base64)
        print(f"shell: VFS load error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch generic loading errors
        print(f"shell: VFS Fatal Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Execute startup script if provided
    if args.startup_script:
        execute_startup_script(args.startup_script, args.vfs_data_path)
        
    # Start the interactive REPL loop
    repl_loop(args.vfs_data_path)

if __name__ == "__main__":
    configure_and_start()

# --- Placeholder functions from Stage 2 kept for completeness ---
def parse_command(command_line):
    if not command_line:
        return []
    try:
        return shlex.split(command_line)
    except ValueError as e:
        print(f"shell: parser error: {e}", file=sys.stderr)
        return []
