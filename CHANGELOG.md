# Changelog

All notable changes to DriveWorks Project Compare are documented in this file.
The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.2] - 2026-06-09

### Added

- Variables table now shows a **Category** column (resolved category name).

### Fixed

- Document **Type** changes are now detected — a type-only change previously
  showed as Unchanged.
- Documents now show a **rule-level breakdown** (which rule changed and how)
  instead of only a rule count.
- Component Tasks now show a rule-level breakdown under each modified task.
- Variables and Constants now also compare store name and comment (shown as
  muted sub-notes); Calculation Tables now compare row count.

### Changed

- Each report section renders independently — one section hitting unexpected
  data degrades to a placeholder instead of failing the whole report.
- A malformed (non-numeric) calculation-table RowIndex is ignored rather than
  aborting the parse.
- `.driveprojx` extraction guards against path traversal (zip slip).
- GUI: extracted temp dirs are cleaned up after each comparison, and the
  launch-time update check no longer errors if the window is closed first.
- Removed the unused `CalcTableCell` model.

## [1.0.1] - 2026-06-09

### Added

- A free, fail-silent update check. On launch (GUI) and after a CLI run, the app
  queries the GitHub Releases API and shows a "newer version available" notice
  linking to the download page. It only notifies — it never downloads or
  installs — and is silent when offline.

### Fixed

- **Flip Direction** no longer corrupts the summary cards. It was swapping the
  card *labels* instead of the counts, leaving a green card labelled "Removed".
  It now swaps the Added/Removed counts and keeps labels and colors fixed.
- **Inline diffs are now token-level** instead of word-level. Because DriveWorks
  formulas rarely contain spaces, any change used to re-highlight the entire
  formula; now only the changed token (number, identifier, operator) lights up.
- **Flip Direction is now consistent for lookup-table grids** — per-cell and
  per-column highlight classes swap, and "New"/"Old" column badges flip too.
- **Duplicate task / component-task names no longer collapse.** Specification
  macro tasks (keyed by title + type) and component tasks (keyed by name +
  component) now disambiguate repeats so a change in a same-named task is not
  silently dropped.
- **No more no-op "Modified" rows.** Navigation steps and form/control
  properties that differ only in a non-displayed field (e.g. the IsStatic flag
  with an unchanged value) are now treated as unchanged.
- **Status filtering no longer orphans grouped rows.** A group's identity row
  (control/task/column name) stays visible whenever any of its child rows pass
  the filter.
- Removed em dashes from the report (the "unchanged" status marker).

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

[1.0.2]: https://github.com/CarbonNapkin/DriveWorksDiff/releases/tag/v1.0.2
[1.0.1]: https://github.com/CarbonNapkin/DriveWorksDiff/releases/tag/v1.0.1
[1.0.0]: https://github.com/CarbonNapkin/DriveWorksDiff/releases/tag/v1.0.0
