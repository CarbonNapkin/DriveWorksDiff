"""
Comparison functions for DriveWorks project elements.
"""

import csv
import io
from difflib import SequenceMatcher
from html import escape


def inline_diff(old: str, new: str) -> str:
    """Generate inline HTML diff showing changes"""
    if old == new:
        return escape(new)
    
    if not old:
        return f'<span class="added">{escape(new)}</span>'
    if not new:
        return f'<span class="removed">{escape(old)}</span>'
    
    # Use SequenceMatcher for word-level diff
    old_words = old.split()
    new_words = new.split()
    
    matcher = SequenceMatcher(None, old_words, new_words)
    result = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            result.append(escape(' '.join(old_words[i1:i2])))
        elif tag == 'replace':
            result.append(f'<span class="removed">{escape(" ".join(old_words[i1:i2]))}</span>')
            result.append(f'<span class="added">{escape(" ".join(new_words[j1:j2]))}</span>')
        elif tag == 'delete':
            result.append(f'<span class="removed">{escape(" ".join(old_words[i1:i2]))}</span>')
        elif tag == 'insert':
            result.append(f'<span class="added">{escape(" ".join(new_words[j1:j2]))}</span>')
    
    return ' '.join(result)


def compare_dicts(old: dict, new: dict) -> tuple[set, set, set]:
    """Compare two dicts, return (added, removed, common) keys"""
    old_keys = set(old.keys())
    new_keys = set(new.keys())
    
    added = new_keys - old_keys
    removed = old_keys - new_keys
    common = old_keys & new_keys
    
    return added, removed, common


def compare_variables(old: dict, new: dict) -> tuple[str, dict]:
    """Compare variables and generate HTML"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for name in sorted(added):
        v = new[name]
        rows.append(f'<tr class="added"><td>{escape(name)}</td><td><span class="badge badge-added">Added</span></td>'
                   f'<td class="formula">{escape(v.formula)}</td></tr>')
    
    for name in sorted(removed):
        v = old[name]
        rows.append(f'<tr class="removed"><td>{escape(name)}</td><td><span class="badge badge-removed">Removed</span></td>'
                   f'<td class="formula">{escape(v.formula)}</td></tr>')
    
    for name in sorted(common):
        old_v, new_v = old[name], new[name]
        if old_v.formula != new_v.formula:
            stats['modified'] += 1
            diff = inline_diff(old_v.formula, new_v.formula)
            rows.append(f'<tr class="modified"><td>{escape(name)}</td><td><span class="badge badge-modified">Modified</span></td>'
                       f'<td class="formula">{diff}</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                       f'<td class="formula">{escape(old_v.formula)}</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Variable Name</th><th>Status</th><th>Formula</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="3" class="empty">No variables found</td></tr>'}</tbody>
    </table>'''
    
    return html, stats


def compare_constants(old: dict, new: dict) -> tuple[str, dict]:
    """Compare constants"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for name in sorted(added):
        c = new[name]
        rows.append(f'<tr class="added"><td>{escape(name)}</td><td><span class="badge badge-added">Added</span></td>'
                   f'<td>{escape(c.value)}</td></tr>')
    
    for name in sorted(removed):
        c = old[name]
        rows.append(f'<tr class="removed"><td>{escape(name)}</td><td><span class="badge badge-removed">Removed</span></td>'
                   f'<td>{escape(c.value)}</td></tr>')
    
    for name in sorted(common):
        old_c, new_c = old[name], new[name]
        if old_c.value != new_c.value:
            stats['modified'] += 1
            diff = inline_diff(old_c.value, new_c.value)
            rows.append(f'<tr class="modified"><td>{escape(name)}</td><td><span class="badge badge-modified">Modified</span></td>'
                       f'<td>{diff}</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                       f'<td>{escape(old_c.value)}</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Constant Name</th><th>Status</th><th>Value</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="3" class="empty">No constants found</td></tr>'}</tbody>
    </table>'''
    
    return html, stats


def compare_special_vars(old: dict, new: dict) -> tuple[str, dict]:
    """Compare special variables"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for name in sorted(added):
        sv = new[name]
        val = sv['rule'] or sv['value']
        rows.append(f'<tr class="added"><td>{escape(name)}</td><td><span class="badge badge-added">Added</span></td>'
                   f'<td class="formula">{escape(val)}</td></tr>')
    
    for name in sorted(removed):
        sv = old[name]
        val = sv['rule'] or sv['value']
        rows.append(f'<tr class="removed"><td>{escape(name)}</td><td><span class="badge badge-removed">Removed</span></td>'
                   f'<td class="formula">{escape(val)}</td></tr>')
    
    for name in sorted(common):
        old_sv, new_sv = old[name], new[name]
        old_val = old_sv['rule'] or old_sv['value']
        new_val = new_sv['rule'] or new_sv['value']
        
        if old_val != new_val:
            stats['modified'] += 1
            diff = inline_diff(old_val, new_val)
            rows.append(f'<tr class="modified"><td>{escape(name)}</td><td><span class="badge badge-modified">Modified</span></td>'
                       f'<td class="formula">{diff}</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                       f'<td class="formula">{escape(old_val)}</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Special Variable</th><th>Status</th><th>Value / Rule</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="3" class="empty">No special variables found</td></tr>'}</tbody>
    </table>'''
    
    return html, stats


def _calc_row(col: str, scope: str, status: str, old_val: str, new_val: str,
              first_in_group: bool = False) -> str:
    """Emit one row of a calculation-table diff. The Column cell is blanked
    on rows after the first row in that column's group, matching the same
    grouping treatment used by Forms and Macros."""
    badge = f'<span class="badge badge-{status}">{status.title()}</span>'
    if status == 'modified':
        diff = inline_diff(old_val, new_val)
    else:
        diff = escape(new_val or old_val)
    cls = f'{status}{" group-start" if first_in_group else ""}'
    col_cell = escape(col) if first_in_group else ''
    return (
        f'<tr class="{cls}"><td class="grouper">{col_cell}</td>'
        f'<td>{escape(scope)}</td>'
        f'<td>{badge}</td><td class="formula">{diff}</td></tr>'
    )


def compare_calc_tables(old: dict, new: dict) -> tuple[str, dict]:
    """Compare calculation tables"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}

    html_parts = []

    for name in sorted(added):
        html_parts.append(
            f'<h3 class="added">➕ {escape(name)} <span class="badge badge-added">Added</span></h3>'
        )

    for name in sorted(removed):
        html_parts.append(
            f'<h3 class="removed">➖ {escape(name)} <span class="badge badge-removed">Removed</span></h3>'
        )

    for name in sorted(common):
        old_tbl, new_tbl = old[name], new[name]
        rows_html = []
        all_cols = set(old_tbl.columns.keys()) | set(new_tbl.columns.keys())

        for col in sorted(all_cols):
            old_col = old_tbl.columns.get(col, {'common': '', 'rows': {}})
            new_col = new_tbl.columns.get(col, {'common': '', 'rows': {}})

            # Buffer this column's rows so we can mark the first row as
            # group-start without knowing ahead of time which row that is.
            col_rows = []

            if col not in old_tbl.columns:
                col_rows.append(('Common', 'added', '', new_col['common']))
                for idx in sorted(new_col['rows']):
                    col_rows.append((f'Row {idx}', 'added', '', new_col['rows'][idx]))
            elif col not in new_tbl.columns:
                col_rows.append(('Common', 'removed', old_col['common'], ''))
                for idx in sorted(old_col['rows']):
                    col_rows.append((f'Row {idx}', 'removed', old_col['rows'][idx], ''))
            else:
                if old_col['common'] != new_col['common']:
                    col_rows.append(('Common', 'modified', old_col['common'], new_col['common']))
                for idx in sorted(set(old_col['rows']) | set(new_col['rows'])):
                    o = old_col['rows'].get(idx, '')
                    n = new_col['rows'].get(idx, '')
                    if o == n:
                        continue
                    if not o:
                        col_rows.append((f'Row {idx}', 'added', '', n))
                    elif not n:
                        col_rows.append((f'Row {idx}', 'removed', o, ''))
                    else:
                        col_rows.append((f'Row {idx}', 'modified', o, n))

            for i, (scope, status, old_v, new_v) in enumerate(col_rows):
                rows_html.append(_calc_row(col, scope, status, old_v, new_v, first_in_group=(i == 0)))

        if rows_html:
            stats['modified'] += 1
            html_parts.append(
                f'<h3 class="modified">📊 {escape(name)} <span class="badge badge-modified">Modified</span></h3>'
                f'<table><thead><tr><th>Column</th><th>Scope</th><th>Status</th><th>Formula</th></tr></thead>'
                f'<tbody>{"".join(rows_html)}</tbody></table>'
            )
        else:
            stats['unchanged'] += 1

    return ''.join(html_parts) if html_parts else '<p class="empty">No calculation tables found</p>', stats


def compare_component_tasks(old: dict, new: dict) -> tuple[str, dict]:
    """Compare component tasks"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for key in sorted(added):
        t = new[key]
        rows.append(f'<tr class="added"><td>{escape(t.name)}</td><td>{escape(t.task_type)}</td>'
                   f'<td><span class="badge badge-added">Added</span></td><td>{escape(t.component_id or t.scope)}</td></tr>')
    
    for key in sorted(removed):
        t = old[key]
        rows.append(f'<tr class="removed"><td>{escape(t.name)}</td><td>{escape(t.task_type)}</td>'
                   f'<td><span class="badge badge-removed">Removed</span></td><td>{escape(t.component_id or t.scope)}</td></tr>')
    
    for key in sorted(common):
        old_t, new_t = old[key], new[key]
        
        # Compare rules
        rule_diff = False
        for rule_name in set(old_t.rules.keys()) | set(new_t.rules.keys()):
            if old_t.rules.get(rule_name) != new_t.rules.get(rule_name):
                rule_diff = True
                break
        
        if rule_diff:
            stats['modified'] += 1
            rows.append(f'<tr class="modified"><td>{escape(old_t.name)}</td><td>{escape(old_t.task_type)}</td>'
                       f'<td><span class="badge badge-modified">Modified</span></td><td>{escape(old_t.component_id or old_t.scope)}</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(old_t.name)}</td><td>{escape(old_t.task_type)}</td>'
                       f'<td>—</td><td>{escape(old_t.component_id or old_t.scope)}</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Task Name</th><th>Type</th><th>Status</th><th>Component/Scope</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="4" class="empty">No component tasks found</td></tr>'}</tbody>
    </table>'''
    
    return html, stats


def compare_documents(old: dict, new: dict) -> tuple[str, dict]:
    """Compare documents/triggered actions"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for name in sorted(added):
        d = new[name]
        rows.append(f'<tr class="added"><td>{escape(name)}</td><td><span class="badge badge-added">Added</span></td>'
                   f'<td>{len(d["rules"])} rules</td></tr>')
    
    for name in sorted(removed):
        d = old[name]
        rows.append(f'<tr class="removed"><td>{escape(name)}</td><td><span class="badge badge-removed">Removed</span></td>'
                   f'<td>{len(d["rules"])} rules</td></tr>')
    
    for name in sorted(common):
        old_d, new_d = old[name], new[name]
        
        if old_d['rules'] != new_d['rules']:
            stats['modified'] += 1
            rows.append(f'<tr class="modified"><td>{escape(name)}</td><td><span class="badge badge-modified">Modified</span></td>'
                       f'<td>{len(new_d["rules"])} rules</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                       f'<td>{len(old_d["rules"])} rules</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Document Name</th><th>Status</th><th>Rules</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="3" class="empty">No documents found</td></tr>'}</tbody>
    </table>'''
    
    return html, stats


def _parse_csv_table(body: str) -> tuple:
    """Parse a CSV string into (headers, rows). Rows are lists of strings."""
    if not body or not body.strip():
        return [], []
    try:
        all_rows = list(csv.reader(io.StringIO(body)))
    except Exception:
        return [], []
    if not all_rows:
        return [], []
    return all_rows[0], all_rows[1:]


def _row_at(row: list, idx: int) -> str:
    """Safe cell access, padding short rows with empty strings."""
    if idx is None or idx < 0 or idx >= len(row):
        return ''
    return row[idx]


def _render_lookup_grid(name: str, top_status: str, old_body: str, new_body: str) -> str:
    """Render one lookup table as a cell-highlighted grid. top_status is the
    table-level status ('added' / 'removed' / 'modified') used to color the
    h3 header. The diff between old_body and new_body decides per-cell
    coloring inside the grid."""
    old_headers, old_rows = _parse_csv_table(old_body)
    new_headers, new_rows = _parse_csv_table(new_body)

    old_set = set(old_headers)
    new_set = set(new_headers)

    # Column display order: new headers first, then any old-only headers at
    # the end so removed columns are visible but do not push everything around.
    display_cols = []
    for h in new_headers:
        display_cols.append((h, 'added' if h not in old_set else 'common'))
    for h in old_headers:
        if h not in new_set:
            display_cols.append((h, 'removed'))

    old_col_idx = {h: i for i, h in enumerate(old_headers)}
    new_col_idx = {h: i for i, h in enumerate(new_headers)}

    # Row keys = first column. If duplicates exist, fall back to row index.
    old_keys = [r[0] if r else '' for r in old_rows]
    new_keys = [r[0] if r else '' for r in new_rows]
    duplicate_keys = (
        len(set(old_keys)) != len(old_keys) or
        len(set(new_keys)) != len(new_keys)
    )

    # Build the diff_rows list. Each entry is (status, old_row_or_None, new_row_or_None).
    diff_rows = []
    if duplicate_keys:
        # Pair by index. Beyond either length, the missing side is None.
        n = max(len(old_rows), len(new_rows))
        for i in range(n):
            o = old_rows[i] if i < len(old_rows) else None
            n_row = new_rows[i] if i < len(new_rows) else None
            if o is None:
                diff_rows.append(('added', None, n_row))
            elif n_row is None:
                diff_rows.append(('removed', o, None))
            elif o == n_row:
                diff_rows.append(('unchanged', o, n_row))
            else:
                diff_rows.append(('modified', o, n_row))
    else:
        old_by_key = dict(zip(old_keys, old_rows))
        new_by_key = dict(zip(new_keys, new_rows))
        for key, new_row in zip(new_keys, new_rows):
            if key in old_by_key:
                old_row = old_by_key[key]
                status = 'unchanged' if old_row == new_row else 'modified'
                diff_rows.append((status, old_row, new_row))
            else:
                diff_rows.append(('added', None, new_row))
        for key, old_row in zip(old_keys, old_rows):
            if key not in new_by_key:
                diff_rows.append(('removed', old_row, None))

    counts = {'added': 0, 'removed': 0, 'modified': 0, 'unchanged': 0}
    for status, *_ in diff_rows:
        counts[status] += 1

    # Header row with per-column status badges
    header_cells = []
    for h, s in display_cols:
        suffix = ''
        if s == 'added':
            suffix = ' <span class="badge badge-added">New</span>'
        elif s == 'removed':
            suffix = ' <span class="badge badge-removed">Old</span>'
        cls = f' class="col-{s}"' if s != 'common' else ''
        header_cells.append(f'<th{cls}>{escape(h)}{suffix}</th>')

    # Body rows
    body_rows = []
    for status, old_row, new_row in diff_rows:
        cells = []
        for h, col_status in display_cols:
            old_idx = old_col_idx.get(h)
            new_idx = new_col_idx.get(h)
            old_val = _row_at(old_row, old_idx) if old_row is not None else ''
            new_val = _row_at(new_row, new_idx) if new_row is not None else ''

            if col_status == 'added':
                # Column only exists in new. Show new value (blank for removed rows).
                cells.append(f'<td class="cell-added">{escape(new_val)}</td>')
            elif col_status == 'removed':
                # Column only exists in old. Show old value (blank for added rows).
                cells.append(f'<td class="cell-removed">{escape(old_val)}</td>')
            else:
                # Common column. Compare cells.
                if status == 'added':
                    cells.append(f'<td>{escape(new_val)}</td>')
                elif status == 'removed':
                    cells.append(f'<td>{escape(old_val)}</td>')
                elif old_val != new_val:
                    cells.append(f'<td class="cell-changed">{inline_diff(old_val, new_val)}</td>')
                else:
                    cells.append(f'<td>{escape(new_val)}</td>')
        body_rows.append(f'<tr class="{status}">{"".join(cells)}</tr>')

    # Header h3 badges show change counts
    sub_badges = ''
    if counts['added']: sub_badges += f' <span class="badge badge-added">+{counts["added"]}</span>'
    if counts['removed']: sub_badges += f' <span class="badge badge-removed">-{counts["removed"]}</span>'
    if counts['modified']: sub_badges += f' <span class="badge badge-modified">~{counts["modified"]}</span>'

    if top_status == 'added':
        icon = '➕'
        label = '<span class="badge badge-added">Added</span>'
    elif top_status == 'removed':
        icon = '➖'
        label = '<span class="badge badge-removed">Removed</span>'
    else:
        icon = '📋'
        label = '<span class="badge badge-modified">Modified</span>'

    dimension_note = (
        f'<small>{len(diff_rows)} rows × {len(display_cols)} cols'
        + (', keyed by row index (duplicate first-column values)' if duplicate_keys else '')
        + '</small>'
    )

    return (
        f'<h3 class="{top_status}">{icon} {escape(name)} {label}{sub_badges} {dimension_note}</h3>'
        f'<table class="lookup-grid"><thead><tr>{"".join(header_cells)}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody></table>'
    )


def compare_lookup_tables(old: dict, new: dict) -> tuple[str, dict]:
    """Compare lookup tables, rendering each modified table as a cell-
    highlighted grid keyed by the first column. Unchanged rows are emitted
    with class="unchanged" so the global lookup-row toggle can hide them."""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    html_parts = []

    for name in sorted(added):
        html_parts.append(_render_lookup_grid(name, 'added', '', new[name]))

    for name in sorted(removed):
        html_parts.append(_render_lookup_grid(name, 'removed', old[name], ''))

    for name in sorted(common):
        if old[name] == new[name]:
            stats['unchanged'] += 1
            continue
        stats['modified'] += 1
        html_parts.append(_render_lookup_grid(name, 'modified', old[name], new[name]))

    body = ''.join(html_parts) if html_parts else '<p class="empty">No lookup tables found</p>'
    return body, stats


def compare_data_tables(old: dict, new: dict) -> tuple[str, dict]:
    """Compare data table definitions (name + type, row data lives elsewhere)."""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    rows = []

    for name in sorted(added):
        d = new[name]
        rows.append(
            f'<tr class="added"><td>{escape(name)}</td>'
            f'<td><span class="badge badge-added">Added</span></td>'
            f'<td>{escape(d.table_type)}</td></tr>'
        )

    for name in sorted(removed):
        d = old[name]
        rows.append(
            f'<tr class="removed"><td>{escape(name)}</td>'
            f'<td><span class="badge badge-removed">Removed</span></td>'
            f'<td>{escape(d.table_type)}</td></tr>'
        )

    for name in sorted(common):
        old_d, new_d = old[name], new[name]
        if old_d.table_type != new_d.table_type:
            stats['modified'] += 1
            rows.append(
                f'<tr class="modified"><td>{escape(name)}</td>'
                f'<td><span class="badge badge-modified">Modified</span></td>'
                f'<td class="formula">{inline_diff(old_d.table_type, new_d.table_type)}</td></tr>'
            )
        else:
            stats['unchanged'] += 1
            rows.append(
                f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                f'<td>{escape(new_d.table_type)}</td></tr>'
            )

    body = ''.join(rows) if rows else '<tr><td colspan="3" class="empty">No data tables found</td></tr>'
    html = (
        '<table><thead><tr><th>Data Table</th><th>Status</th><th>Type</th></tr></thead>'
        f'<tbody>{body}</tbody></table>'
    )
    return html, stats


def compare_nav_steps(old: dict, new: dict) -> tuple[str, dict]:
    """Compare navigation steps (the form flow graph)."""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    rows = []

    def fmt_target(s):
        # Highlight the resolved Next/Previous wiring as a compact string.
        bits = []
        if s.next_step_value:
            bits.append(f'next={s.next_step_value}')
        if s.next_step_rule and s.next_step_rule != f'"{s.next_step_value}"':
            bits.append(f'nextRule={s.next_step_rule}')
        if s.next_macro_value:
            bits.append(f'nextMacro={s.next_macro_value}')
        if s.previous_macro_value:
            bits.append(f'prevMacro={s.previous_macro_value}')
        return ', '.join(bits)

    for name in sorted(added):
        s = new[name]
        rows.append(
            f'<tr class="added"><td>{escape(name)}</td><td>{escape(s.step_type)}</td>'
            f'<td><span class="badge badge-added">Added</span></td>'
            f'<td class="formula">{escape(fmt_target(s))}</td></tr>'
        )

    for name in sorted(removed):
        s = old[name]
        rows.append(
            f'<tr class="removed"><td>{escape(name)}</td><td>{escape(s.step_type)}</td>'
            f'<td><span class="badge badge-removed">Removed</span></td>'
            f'<td class="formula">{escape(fmt_target(s))}</td></tr>'
        )

    for name in sorted(common):
        o, n = old[name], new[name]
        if o != n:
            stats['modified'] += 1
            diff = inline_diff(fmt_target(o), fmt_target(n))
            type_cell = escape(n.step_type) if o.step_type == n.step_type else inline_diff(o.step_type, n.step_type)
            rows.append(
                f'<tr class="modified"><td>{escape(name)}</td><td>{type_cell}</td>'
                f'<td><span class="badge badge-modified">Modified</span></td>'
                f'<td class="formula">{diff}</td></tr>'
            )
        else:
            stats['unchanged'] += 1
            rows.append(
                f'<tr class="unchanged"><td>{escape(name)}</td><td>{escape(n.step_type)}</td>'
                f'<td>—</td><td class="formula">{escape(fmt_target(n))}</td></tr>'
            )

    body = ''.join(rows) if rows else '<tr><td colspan="4" class="empty">No navigation steps found</td></tr>'
    html = (
        '<table><thead><tr><th>Step</th><th>Type</th><th>Status</th><th>Wiring</th></tr></thead>'
        f'<tbody>{body}</tbody></table>'
    )
    return html, stats


def compare_spec_macros(old: dict, new: dict) -> tuple[str, dict]:
    """Compare Specification Macros at the macro level, with task-level
    add/remove/modify rows under each modified macro."""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    html_parts = []

    def task_label(t):
        return f'{t.title or "(untitled)"} [{t.task_type or "?"}]'

    for name in sorted(added):
        m = new[name]
        html_parts.append(
            f'<h3 class="added">➕ {escape(name)} <span class="badge badge-added">Added</span> '
            f'<small>({len(m.tasks)} tasks)</small></h3>'
        )

    for name in sorted(removed):
        m = old[name]
        html_parts.append(
            f'<h3 class="removed">➖ {escape(name)} <span class="badge badge-removed">Removed</span> '
            f'<small>({len(m.tasks)} tasks)</small></h3>'
        )

    for name in sorted(common):
        o, n = old[name], new[name]
        # Task identity is title + task_type. Position matters too (order),
        # but we surface order by listing tasks in source order with positions.
        old_keys = [task_label(t) for t in o.tasks]
        new_keys = [task_label(t) for t in n.tasks]

        old_by_key = {k: t for k, t in zip(old_keys, o.tasks)}
        new_by_key = {k: t for k, t in zip(new_keys, n.tasks)}

        all_keys = list(dict.fromkeys(old_keys + new_keys))  # preserve first-seen order
        row_html = []
        macro_modified = False

        for key in all_keys:
            ot = old_by_key.get(key)
            nt = new_by_key.get(key)
            if ot is None:
                macro_modified = True
                row_html.append(_macro_task_rows(key, 'added', None, nt))
            elif nt is None:
                macro_modified = True
                row_html.append(_macro_task_rows(key, 'removed', ot, None))
            else:
                prop_changes = _diff_props(ot.properties, nt.properties)
                if prop_changes:
                    macro_modified = True
                    row_html.append(_macro_task_rows(key, 'modified', ot, nt, prop_changes))

        if old_keys != new_keys and not macro_modified:
            # Task set identical but reordered.
            macro_modified = True
            row_html.append(
                '<tr class="modified"><td colspan="3"><em>Tasks reordered</em></td>'
                f'<td class="formula">old order: {escape(", ".join(old_keys))}<br>'
                f'new order: {escape(", ".join(new_keys))}</td></tr>'
            )

        if macro_modified:
            stats['modified'] += 1
            html_parts.append(
                f'<h3 class="modified">⚙️ {escape(name)} <span class="badge badge-modified">Modified</span></h3>'
                '<table><thead><tr><th>Task</th><th>Status</th><th>Property</th><th>Formula</th></tr></thead>'
                f'<tbody>{"".join(row_html)}</tbody></table>'
            )
        else:
            stats['unchanged'] += 1

    body = ''.join(html_parts) if html_parts else '<p class="empty">No specification macros found</p>'
    return body, stats


def _diff_props(old_props: dict, new_props: dict) -> list:
    """Return list of (prop_name, status, old_val, new_val) tuples for prop
    keys that differ between the two property dicts."""
    out = []
    all_keys = sorted(set(old_props) | set(new_props))
    for k in all_keys:
        o = old_props.get(k, '')
        n = new_props.get(k, '')
        if o == n:
            continue
        if k not in old_props:
            out.append((k, 'added', '', n))
        elif k not in new_props:
            out.append((k, 'removed', o, ''))
        else:
            out.append((k, 'modified', o, n))
    return out


def _fmt_prop(p):
    """Format a (is_static, value) tuple for display."""
    if p is None:
        return ''
    _is_static, val = p
    return val or ''


def _compare_prop_dicts(old_props: dict, new_props: dict) -> list:
    """Compare two property dicts whose values are (is_static, formula_or_value)
    tuples. Returns list of (prop_name, status, old_tuple, new_tuple) for
    properties whose tuples differ. Empty-vs-empty pairs are skipped, even
    when is_static differs, to keep the report focused on real changes."""
    out = []
    for k in sorted(set(old_props) | set(new_props)):
        o = old_props.get(k)
        n = new_props.get(k)
        if o == n:
            continue
        o_val = _fmt_prop(o)
        n_val = _fmt_prop(n)
        if not o_val and not n_val:
            # Both effectively empty (likely a static-flag-only change). Skip
            # to keep the diff readable on real-world projects.
            continue
        if k not in old_props or o_val == '':
            out.append((k, 'added', o, n))
        elif k not in new_props or n_val == '':
            out.append((k, 'removed', o, n))
        else:
            out.append((k, 'modified', o, n))
    return out


def _form_change_row(control: str, ctrl_type: str, prop: str, status: str,
                     old_p, new_p, first_in_group: bool = True) -> str:
    """Render one property change row. Only the first row in a control's group
    shows the control name and type; later rows blank those cells so the
    repeated identity does not visually drown out the per-property changes."""
    badge = f'<span class="badge badge-{status}">{status.title()}</span>'
    old_v = _fmt_prop(old_p)
    new_v = _fmt_prop(new_p)
    if status == 'modified':
        cell = inline_diff(old_v, new_v)
    else:
        cell = escape(new_v or old_v)
    classes = status + (' group-start' if first_in_group else '')
    name_cell = escape(control) if first_in_group else ''
    type_cell = escape(ctrl_type) if first_in_group else ''
    return (
        f'<tr class="{classes}">'
        f'<td class="grouper">{name_cell}</td>'
        f'<td class="grouper">{type_cell}</td>'
        f'<td>{escape(prop)}</td>'
        f'<td>{badge}</td>'
        f'<td class="formula">{cell}</td>'
        '</tr>'
    )


def compare_forms(old: dict, new: dict) -> tuple[str, dict]:
    """Compare Forms and their controls. Each modified form gets a table of
    property-level change rows covering both form-level rules and per-control
    properties."""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    html_parts = []

    for name in sorted(added):
        f = new[name]
        html_parts.append(
            f'<h3 class="added">➕ {escape(name)} <span class="badge badge-added">Added</span> '
            f'<small>({len(f.controls)} controls)</small></h3>'
        )

    for name in sorted(removed):
        f = old[name]
        html_parts.append(
            f'<h3 class="removed">➖ {escape(name)} <span class="badge badge-removed">Removed</span> '
            f'<small>({len(f.controls)} controls)</small></h3>'
        )

    for name in sorted(common):
        of, nf = old[name], new[name]
        change_rows = []

        # Form-level property changes form a single group keyed on "(form)".
        form_prop_changes = _compare_prop_dicts(of.form_props, nf.form_props)
        for i, (prop, status, op, np) in enumerate(form_prop_changes):
            change_rows.append(_form_change_row(
                '(form-level rules)', 'Form', prop, status, op, np,
                first_in_group=(i == 0),
            ))

        c_added, c_removed, c_common = compare_dicts(of.controls, nf.controls)

        for ctrl_name in sorted(c_added):
            c = nf.controls[ctrl_name]
            badge = '<span class="badge badge-added">Added</span>'
            change_rows.append(
                f'<tr class="added group-start">'
                f'<td class="grouper">{escape(ctrl_name)}</td>'
                f'<td class="grouper">{escape(c.control_type)}</td>'
                f'<td colspan="2">{badge}</td>'
                f'<td>{len(c.props)} properties</td></tr>'
            )

        for ctrl_name in sorted(c_removed):
            c = of.controls[ctrl_name]
            badge = '<span class="badge badge-removed">Removed</span>'
            change_rows.append(
                f'<tr class="removed group-start">'
                f'<td class="grouper">{escape(ctrl_name)}</td>'
                f'<td class="grouper">{escape(c.control_type)}</td>'
                f'<td colspan="2">{badge}</td>'
                f'<td>{len(c.props)} properties</td></tr>'
            )

        for ctrl_name in sorted(c_common):
            o_ctrl = of.controls[ctrl_name]
            n_ctrl = nf.controls[ctrl_name]
            type_changed = o_ctrl.control_type != n_ctrl.control_type
            prop_changes = _compare_prop_dicts(o_ctrl.props, n_ctrl.props)
            if not type_changed and not prop_changes:
                continue

            first_done = False

            if type_changed:
                # First row of the group is the type-swap notice; later prop
                # rows are blank in the name/type cells.
                badge = '<span class="badge badge-modified">Type changed</span>'
                change_rows.append(
                    f'<tr class="modified group-start">'
                    f'<td class="grouper">{escape(ctrl_name)}</td>'
                    f'<td class="grouper formula">{inline_diff(o_ctrl.control_type, n_ctrl.control_type)}</td>'
                    f'<td>(control type)</td>'
                    f'<td>{badge}</td>'
                    f'<td></td></tr>'
                )
                first_done = True

            for prop, status, op, np in prop_changes:
                change_rows.append(_form_change_row(
                    ctrl_name, n_ctrl.control_type, prop, status, op, np,
                    first_in_group=not first_done,
                ))
                first_done = True

        if change_rows:
            stats['modified'] += 1
            html_parts.append(
                f'<h3 class="modified">📝 {escape(name)} <span class="badge badge-modified">Modified</span></h3>'
                '<table class="grouped"><thead><tr><th>Control</th><th>Type</th><th>Property</th>'
                '<th>Status</th><th>Formula / Value</th></tr></thead>'
                f'<tbody>{"".join(change_rows)}</tbody></table>'
            )
        else:
            stats['unchanged'] += 1

    body = ''.join(html_parts) if html_parts else '<p class="empty">No forms found</p>'
    return body, stats


def _macro_task_rows(task_key: str, status: str, old_task, new_task, prop_changes=None) -> str:
    """Render one or more <tr> rows for a single macro task."""
    badge = f'<span class="badge badge-{status}">{status.title()}</span>'
    if status == 'added' or status == 'removed':
        t = new_task if status == 'added' else old_task
        n_props = len(t.properties)
        return (
            f'<tr class="{status} group-start"><td class="grouper">{escape(task_key)}</td>'
            f'<td>{badge}</td><td colspan="2">{n_props} properties</td></tr>'
        )
    # Modified case, emit one row per changed property. First row carries the
    # task name and a group-start marker so the table groups visually.
    rows = []
    first = True
    for prop_name, p_status, old_val, new_val in prop_changes or []:
        p_badge = f'<span class="badge badge-{p_status}">{p_status.title()}</span>'
        if p_status == 'modified':
            cell = inline_diff(old_val, new_val)
        else:
            cell = escape(new_val or old_val)
        task_cell = escape(task_key) if first else ''
        status_cell = badge if first else ''
        cls = f'{p_status}{" group-start" if first else ""}'
        rows.append(
            f'<tr class="{cls}"><td class="grouper">{task_cell}</td><td>{status_cell}</td>'
            f'<td>{escape(prop_name)} {p_badge}</td><td class="formula">{cell}</td></tr>'
        )
        first = False
    return ''.join(rows)
