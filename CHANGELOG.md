# Changelog

All notable changes to DriveWorks Project Compare are documented in this file.
The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2026-05-15

First public release. Compares two DriveWorks projects and generates a
self-contained HTML diff report.

### Added

- Direct `.driveprojx` support, files are auto-extracted to a temp directory.
- Recursive scanning, all `project.xml`, `designMaster.xml`, `componentTasks.xml`,
  and `.tdm` files in nested folders are picked up.
- Sections covered in the report:
  - Variables (with resolved category names)
  - Constants
  - Special Variables
  - Calculation Tables, including row-level rules
  - Component Tasks
  - Documents
  - Lookup Tables, rendered as cell-highlighted grids
  - Data Tables
  - Specification Macros, per-task and per-property
  - Navigation Steps
  - Forms, form-level rules plus per-control property formulas
- Hierarchical diff rendering. Forms, Macros, and Calculation Tables emit
  grouped rows where the parent identifier (control, task, column) appears
  once per group, with a visual separator between groups.
- Interactive HTML report:
  - Sticky filter bar with status filters, search, flip-direction, and toggles
    for "Show unchanged sections" and "Show unchanged lookup rows".
  - Sticky per-form and per-table sub-headers stay pinned while you scroll.
  - Auto-collapsed sections for empty diffs, click to expand.
- Three launch modes:
  - CLI, `python -m dw_compare ...`
  - GUI, `python -m dw_compare --gui` or double-click `run_compare.command`
    on macOS
  - Auto-detect, run with no args inside a folder containing two projects
- Tkinter GUI with file and folder pickers, live log pane, and a
  background worker so the window stays responsive.
- Help menu with Documentation link and an About dialog.
- `--version` flag on the CLI.
- Self-contained HTML output suitable for sharing by email or hosting on
  an internal share.

[1.0.0]: https://github.com/CarbonNapkin/DriveWorksDiff/releases/tag/v1.0.0
