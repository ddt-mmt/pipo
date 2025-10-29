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

## Usage

Because `pipo` is installed globally, **you can run it from any directory** (e.g., `/root`, `/home`, etc.). You just need to tell it which project you want to scan.

**Scenario 1: Scanning the directory you are currently in**

If you are already inside the project you want to scan, simply run `pipo` without any arguments.

```bash
# Navigate to your project directory
cd /path/to/your/project

# Run pipo to scan the current directory
pipo
```

**Scenario 2: Scanning a specific directory from anywhere**

You can also tell `pipo` the exact path of the project you want to scan, regardless of your current location.

```bash
# You can be in any directory, for example, your home directory
cd ~

# Tell pipo to scan a specific project path
pipo /root/projek-migrasi
```

In both cases, the resulting `requirements.txt` file will be created inside the scanned project directory (e.g., inside `/path/to/your/project` or `/root/projek-migrasi`).

## Command-Line Options

*   `pipo --help` or `pipo -h`
    *   Shows the help message with all available commands and options.

*   `pipo --version` or `pipo -v`
    *   Shows the currently installed version of `pipo`.
