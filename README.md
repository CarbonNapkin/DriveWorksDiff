# DriveWorks Project Compare

A command-line tool to compare two versions of a DriveWorks project and generate an interactive HTML report showing all differences.

## Features

- **Recursive scanning** - Finds all DriveWorks XML files in nested folders
- **Compares everything** - Variables, Constants, Special Variables, Calculation Tables, Component Tasks, Documents, Lookup Tables
- **Inline diffs** - See exactly what changed in formulas
- **Interactive filtering** - Filter by Added/Removed/Modified/Unchanged
- **Search** - Find specific variables or formulas
- **Flip direction** - Swap old↔new perspective with one click
- **Auto-detect folders** - Just drop two project folders next to the script and run

## Installation

No dependencies required — just Python 3.10+.

```bash
git clone https://github.com/CarbonNapkin/DriveWorksDiff.git
cd DriveWorksDiff
```

## Usage

### Option 1: Auto-detect folders

Place your two project folders alongside the package:

```
my-comparison/
├── dw_compare/
├── run_compare.command
├── prod/           ← old project
└── dev/            ← new project
```

Then run:

```bash
python3 -m dw_compare
```

The tool recognizes folder pairs like: `old/new`, `prod/dev`, `v1/v2`, `before/after`, or any two folders.

### Option 2: Specify folders

```bash
python3 -m dw_compare path/to/old_project path/to/new_project -o report.html
```

### Option 3: Double-click (Mac)

After downloading, run once in Terminal:
```bash
chmod +x run_compare.command
```

Then double-click `run_compare.command` to run.

## Command Line Options

```
python3 -m dw_compare [old_folder] [new_folder] [options]

Arguments:
  old_folder          Path to old project folder (optional if auto-detect works)
  new_folder          Path to new project folder (optional if auto-detect works)

Options:
  -o, --output FILE   Output HTML file (default: dw_comparison.html)
  --no-open           Don't auto-open report in browser
```

## Supported File Types

The tool parses:

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
