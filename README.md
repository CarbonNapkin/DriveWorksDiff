# DriveWorks Project Compare

A command-line tool to compare two versions of a DriveWorks project and generate an interactive HTML report showing all differences.

## Features

- **Direct .driveprojx support** - Pass project files directly, no manual extraction needed
- **Recursive scanning** - Finds all DriveWorks XML files in nested folders
- **Compares everything** - Variables, Constants, Special Variables, Calculation Tables, Component Tasks, Documents, Lookup Tables
- **Inline diffs** - See exactly what changed in formulas
- **Interactive filtering** - Filter by Added/Removed/Modified/Unchanged
- **Search** - Find specific variables or formulas
- **Flip direction** - Swap old↔new perspective with one click
- **Auto-detect projects** - Just drop two project files/folders next to the script and run

## Installation

No dependencies required — just Python 3.10+.

```bash
git clone https://github.com/CarbonNapkin/DriveWorksDiff.git
cd DriveWorksDiff
```

## Usage

### Graphical UI

Launch a simple file-picker UI (no command line needed):

```bash
python3 -m dw_compare --gui
```

On macOS, double-clicking `run_compare.command` opens the GUI.

### Compare .driveprojx files directly

```bash
python3 -m dw_compare old_project.driveprojx new_project.driveprojx
```

### Auto-detect projects

Place your two projects (folders or .driveprojx files) alongside the package:

```
my-comparison/
├── dw_compare/
├── run_compare.command
├── MyProject_v1.driveprojx    ← old project
└── MyProject_v2.driveprojx    ← new project
```

Then run:

```bash
python3 -m dw_compare
```

The tool recognizes patterns like: `old/new`, `prod/dev`, `v1/v2`, `before/after`, or any two projects.

### Specify folders

```bash
python3 -m dw_compare path/to/old_folder path/to/new_folder -o report.html
```

### Double-click (Mac)

Opens the GUI. After downloading, run once in Terminal:
```bash
chmod +x run_compare.command
```

Then double-click `run_compare.command` to run.

## Command Line Options

```
python3 -m dw_compare [old_project] [new_project] [options]

Arguments:
  old_project         Path to old project folder or .driveprojx file
  new_project         Path to new project folder or .driveprojx file

Options:
  -o, --output FILE   Output HTML file (default: dw_comparison.html)
  --no-open           Don't auto-open report in browser
```

## Supported File Types

The tool parses:

- `.driveprojx` - DriveWorks project files (automatically extracted)
- `project.xml` - Variables, Calculation Tables, Documents
- `designMaster.xml` - Constants, Special Variables, Lookup Tables
- `*.tdm` - Team Design Master exports (attribute-based XML format)
- `componentTasks.xml` - Component Tasks and their rules

## Project Structure

```
dw_compare/
├── __init__.py      # Package exports
├── __main__.py      # CLI entry point
├── models.py        # Data classes (Variable, Constant, etc.)
├── parsers.py       # XML parsing functions
├── comparers.py     # Comparison and diff logic
└── report.py        # HTML report generation
```

## Building as Standalone App

To create a double-clickable app (no Python required for end users):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed dw_compare/__main__.py -n dw_compare
```

This creates `dist/dw_compare` (Mac) or `dist/dw_compare.exe` (Windows).

## License

MIT

## Author

[Base 10 Consultants](https://base10consultants.com) - DriveWorks Authorized Service Partner
