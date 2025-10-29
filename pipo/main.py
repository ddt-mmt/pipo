import os
import ast
import argparse
import sys
import importlib.metadata
import subprocess
from pyfiglet import Figlet
from colorama import Fore, Style, init

def get_std_libs():
    """Fetches the list of standard library modules for the current Python version."""
    # In a real-world scenario, we might use a pre-compiled list for a specific Python version
    # or use more sophisticated methods. For this tool, we'll use a known list.
    # This list is for Python 3.10. A more robust tool would adjust this based on the Python version.
    try:
        from stdlib_list import stdlib_list
        return set(stdlib_list("3.10"))
    except ImportError:
        print("Warning: 'stdlib-list' not found. Falling back to a basic list. Please run 'pip install stdlib-list' for better accuracy.", file=sys.stderr)
        # A fallback list if stdlib_list is not available
        return {
            "os", "sys", "ast", "argparse", "time", "datetime", "math", "random", "json",
            "re", "subprocess", "collections", "functools", "itertools", "pathlib", "socket",
            "select", "string", "traceback", "unittest", "urllib", "logging", "threading", "importlib"
            # This is not exhaustive and is a limitation of the fallback.
        }


def find_imports(path):
    """Find all imported modules in a given Python file using AST."""
    imports = set()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get the top-level module (e.g., 'os.path' -> 'os')
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                # Ignore relative imports (e.g., from . import foo)
                if node.level > 0:
                    continue
                if node.module:
                    imports.add(node.module.split('.')[0])
    except Exception as e:
        print(f"Error parsing {path}: {e}", file=sys.stderr)
    return imports

def _update_pipo():
    """Updates the pipo tool by pulling from git and reinstalling."""
    pipo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(f"{Fore.CYAN}Updating pipo from {pipo_dir}...{Style.RESET_ALL}")

    try:
        # Git pull
        print(f"{Fore.YELLOW}Pulling latest changes from Git...{Style.RESET_ALL}")
        subprocess.run(["git", "pull", "origin", "master"], cwd=pipo_dir, check=True)
        print(f"{Fore.GREEN}Git pull successful.{Style.RESET_ALL}")

        # Pip reinstall
        print(f"{Fore.YELLOW}Reinstalling pipo with updated dependencies...{Style.RESET_ALL}")
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", pipo_dir], check=True)
        print(f"{Fore.GREEN}pipo updated successfully!{Style.RESET_ALL}")

    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error during update: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

def _uninstall_pipo():
    """Uninstalls the pipo tool."""
    print(f"{Fore.CYAN}Uninstalling pipo...{Style.RESET_ALL}")
    try:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "pipo", "-y"], check=True)
        print(f"{Fore.GREEN}pipo uninstalled successfully!{Style.RESET_ALL}\n")
        print(f"{Fore.YELLOW}Note: If pipo was installed in editable mode, its directory still exists.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error during uninstallation: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

def _dockerize_project(path, app_type, main_file, port):
    """Generates a Dockerfile for the project."""
    dockerfile_content = """
# Use the official Python image as a base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Salin file requirements.txt dan instal dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin sisa kode aplikasi
COPY . .

# Ekspos port yang digunakan aplikasi (misal: 5000 untuk Flask)
EXPOSE {port}

# Perintah untuk menjalankan aplikasi
CMD ["gunicorn", "--bind", "0.0.0.0:{port}", "{main_file}:app"]
""".format(port=port, main_file=main_file.replace('.py', ''))

    output_path = os.path.join(path, 'Dockerfile')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        print(f"{Fore.GREEN}Dockerfile successfully generated at {output_path}{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}Error writing Dockerfile to {output_path}: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

def _dockerize_project(args): # args parameter used directly
    """Generates a Dockerfile for the project."""
    path = os.path.abspath(args.path)
    if not os.path.isdir(path):
        print(f"{Fore.RED}Error: Path '{path}' is not a valid directory.{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

    app_type = args.app_type
    main_file = args.main_file
    port = args.port

    # Basic Dockerfile content
    dockerfile_content = f"""
# Use the official Python image as a base image
FROM python:3.10-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
# Note: Pipo expects requirements.txt to be already generated by 'pipo scan'
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port the application uses
EXPOSE {port}
"""
    # Customize CMD based on app_type
    if app_type == 'flask':
        # Assumes the Flask app object is named 'app' in the main_file
        # main_file 'app.py' becomes 'app' module
        dockerfile_content += f'\n# Command to run the Flask application with Gunicorn\nCMD ["gunicorn", "--bind", "0.0.0.0:{port}", "{main_file.replace(".py", "")}:app"]'
    elif app_type == 'django': # Placeholder, more complex normally
        # Assumes standard Django project structure and wsgi.py
        dockerfile_content += f'\n# Command to run the Django application with Gunicorn\nCMD ["gunicorn", "--bind", "0.0.0.0:{port}", "{main_file.replace(".py", "")}.wsgi:application"]'
    elif app_type == 'script':
        dockerfile_content += f'\n# Command to run the Python script\nCMD ["python", "{main_file}"]'
    else: # Fallback to generic simple script command
        print(f"{Fore.YELLOW}Warning: Unknown app_type '{app_type}'. Using generic Python script command.{Style.RESET_ALL}", file=sys.stderr)
        dockerfile_content += f'\n# Command to run the Python application (generic fallback)\nCMD ["python", "{main_file}"]'


    output_path = os.path.join(path, f'Dockerfile')
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        print(f"{Fore.GREEN}Dockerfile successfully generated at {output_path}{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}Error writing Dockerfile to {output_path}: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

def run_scan_command(args): # Scan logic extracted to a function
    """Scans a project for imports and generates requirements.txt."""
    project_path = os.path.abspath(args.path)
    if not os.path.isdir(project_path):
        print(f"{Fore.RED}Error: Path '{project_path}' is not a valid directory.{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)

    print(f"{Fore.CYAN}Scanning project at: {project_path}{Style.RESET_ALL}")

    all_imports = set()
    for root, _, files in os.walk(project_path):
        # A simple way to exclude common virtual environment folders
        if 'venv' in root or 'env' in root or '.git' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                all_imports.update(find_imports(file_path))

    std_libs = get_std_libs()
    external_imports = sorted(list(all_imports - std_libs))

    output_path = os.path.join(project_path, 'requirements.txt')
    print(f"Found {len(external_imports)} external dependencies.")

    if not external_imports:
        print("No external dependencies found. Nothing to write.")
        # If no requirements.txt is needed, ensure we don't accidentally create an empty one
        if os.path.exists(output_path):
            os.remove(output_path) # Clean up existing empty requirements.txt if present
            print(f"Removed empty requirements.txt at {output_path}")
        return

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for lib in external_imports:
                f.write(f"{lib}\\n")
        print(f"{Fore.GREEN}Successfully wrote requirements.txt to {output_path}{Style.RESET_ALL}")
    except IOError as e:
        print(f"{Fore.RED}Error writing to {output_path}: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the pipo CLI tool."""
    init(autoreset=True) # Initialize Colorama

    try:
        version = importlib.metadata.version('pipo')
    except importlib.metadata.PackageNotFoundError:
        version = '0.0.1' # Fallback version if package is not installed

    # Generate and print banner
    f = Figlet(font='slant')
    print(Fore.CYAN + f.renderText('pipo') + Style.RESET_ALL)
    print(Fore.GREEN + "A modern tool to generate requirements.txt for a Python project." + Style.RESET_ALL)
    print(Fore.YELLOW + f"Version: {version}\\n" + Style.RESET_ALL)

    parser = argparse.ArgumentParser(
        description="A modern tool to generate requirements.txt for a Python project.",
        epilog="Visit https://github.com/ddt-mmt/pipo for more information."
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {version}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    subparsers.required = True # Make subcommand mandatory
    

    # Scan command, set as default if no subcommand is provided.
    # If a default is needed when no command is provided,
    # the main parser\'s set_defaults(func=...) should be used in conjunction
    # with the subparsers.
    scan_parser = subparsers.add_parser('scan', help='Scan a project and generate requirements.txt')
    scan_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='The path to the Python project directory (defaults to the current directory).'
    )
    scan_parser.set_defaults(func=run_scan_command) # Set default function for scan


    # Update command
    update_parser = subparsers.add_parser('update', help='Update the pipo tool to the latest version')
    update_parser.set_defaults(func=_update_pipo)

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall the pipo tool')
    uninstall_parser.set_defaults(func=_uninstall_pipo)


    # Dockerize command
    dockerize_parser = subparsers.add_parser('dockerize', help='Generate a Dockerfile for a Python project')
    dockerize_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='The path to the project directory where the Dockerfile will be generated (defaults to current directory).'
    )
    dockerize_parser.add_argument(
        '--app-type',
        default='flask',
        choices=['flask', 'django', 'script'],
        help='Type of Python application (e.g., flask, django, script). Default is flask.'
    )
    dockerize_parser.add_argument(
        '--main-file',
        default='app.py',
        help='The main application file (e.g., app.py, manage.py). Default is app.py.'
    )
    dockerize_parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='The port your application listens on. Default is 5000.'
    )
    dockerize_parser.set_defaults(func=_dockerize_project) # Set default function for dockerize


    
    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    else:
        # If no subcommand is specified, and no default func set for main parser.
        # This occurs if subparsers.required is False and no subcommand is given.
        # But we set subparsers.required = True, so this else block might not be reached directly.
        # However, for robustness or future changes, it's good to have a catch or error out.
        parser.print_help()


if __name__ == "__main__":
    main()
