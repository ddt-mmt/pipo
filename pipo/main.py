import os
import ast
import argparse
import sys
import importlib.metadata

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

def main():
    """Main entry point for the pipo CLI tool."""
    try:
        version = importlib.metadata.version('pipo')
    except importlib.metadata.PackageNotFoundError:
        version = '0.0.1' # Fallback version if package is not installed

    parser = argparse.ArgumentParser(
        description="A modern tool to generate requirements.txt for a Python project.",
        epilog="Visit https://github.com/ddt-mmt/pipo for more information."
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version=f'%(prog)s {version}'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='The path to the Python project directory (defaults to the current directory).'
    )
    args = parser.parse_args()

    project_path = os.path.abspath(args.path)
    if not os.path.isdir(project_path):
        print(f"Error: Path '{project_path}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Scanning project at: {project_path}")

    all_imports = set()
    for root, _, files in os.walk(project_path):
        # A simple way to exclude common virtual environment folders
        if 'venv' in root or 'env' in root or '.git' in root:
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
        return

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for lib in external_imports:
                f.write(f"{lib}\n")
        print(f"Successfully wrote requirements.txt to {output_path}")
    except IOError as e:
        print(f"Error writing to {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
