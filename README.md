# pipo

A modern tool to generate `requirements.txt` for a Python project, inspired by `pipreqs`.

`pipo` scans a project directory, analyzes all Python files for their imports, and generates a clean `requirements.txt` file containing only the external dependencies.

## How it Works

The tool uses Python's built-in `ast` (Abstract Syntax Tree) module to safely and accurately parse Python files. It identifies all `import` and `from ... import` statements, filters out standard library modules, and writes the result to a file.

## Installation

To install the tool from the local source code, you can run `pip` from the directory containing the `pipo` folder (e.g., from `/root` if your project is in `/root/pipo`):

```bash
# We recommend installing in "editable" mode for development
pip install -e ./pipo
```

Once installed, `pipo` becomes a global command available in your terminal.

## Global Options

These options can be used with `pipo` or any of its subcommands.

*   `pipo --help` or `pipo -h`
    *   Shows the help message with all available commands and options.

*   `pipo --version` or `pipo -v`
    *   Shows the currently installed version of `pipo`.

## Commands

`pipo` provides several commands to manage your Python projects.

### `pipo scan [path]`

Scans a Python project directory and generates a `requirements.txt` file based on its imports. If `path` is not provided, it scans the current directory.

**Usage:**

```bash
# Scan the current directory
pipo scan

# Scan a specific directory (e.g., your project at /root/my_project)
pipo scan /root/my_project
```

In both cases, the resulting `requirements.txt` file will be created inside the scanned project directory.

### `pipo update`

Updates the `pipo` tool to the latest version by pulling changes from its Git repository and reinstalling it.

**Usage:**

```bash
pipo update
```

### `pipo uninstall`

Uninstalls the `pipo` tool from your system.

**Usage:**

```bash
pipo uninstall
```

### `pipo dockerize [path] [--app-type {flask,django,script}] [--main-file MAIN_FILE] [--port PORT]`

Generates a basic `Dockerfile` for a Python project. If `path` is not provided, it generates the Dockerfile in the current directory.

**Arguments:**

*   `path`: The path to the project directory where the Dockerfile will be generated (defaults to current directory).
*   `--app-type`: Type of Python application (choices: `flask`, `django`, `script`). Default is `flask`.
*   `--main-file`: The main application file (e.g., `app.py`, `manage.py`). Default is `app.py`.
*   `--port`: The port your application listens on. Default is `5000`.

**Usage Examples:**

```bash
# Generate Dockerfile for a Flask app in the current directory (default settings)
pipo dockerize

# Generate Dockerfile for a Django app in a specific project folder
pipo dockerize /path/to/my_django_project --app-type django --main-file manage.py --port 8000

# Generate Dockerfile for a simple Python script
pipo dockerize ./my_script_project --app-type script --main-file run.py
```
