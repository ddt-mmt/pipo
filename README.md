# pipo

A modern tool to generate `requirements.txt` for a Python project, inspired by `pipreqs`.

`pipo` scans a project directory, analyzes all Python files for their imports, and generates a clean `requirements.txt` file containing only the external dependencies.

## How it works

The tool uses Python's built-in `ast` (Abstract Syntax Tree) module to safely and accurately parse Python files. It identifies all `import` and `from ... import` statements, filters out standard library modules, and writes the result to a file.

## Installation

To install the tool from the local source code, navigate to the parent directory of the `pipo` project and run:

```bash
pip install -e ./pipo
```

(The `-e` flag installs it in "editable" mode, which is useful for development.)

## Usage

Once installed, you can run the tool from your terminal:

```bash
# Scan the current directory
pipo

# Scan a specific directory
pipo /path/to/your/project
```
