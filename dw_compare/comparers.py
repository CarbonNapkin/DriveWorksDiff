"""
Comparison functions for DriveWorks project elements.
"""

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


def _calc_row(col: str, scope: str, status: str, old_val: str, new_val: str) -> str:
    badge = f'<span class="badge badge-{status}">{status.title()}</span>'
    if status == 'modified':
        diff = inline_diff(old_val, new_val)
    else:
        diff = escape(new_val or old_val)
    return (
        f'<tr class="{status}"><td>{escape(col)}</td><td>{escape(scope)}</td>'
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

            if col not in old_tbl.columns:
                rows_html.append(_calc_row(col, 'Common', 'added', '', new_col['common']))
                for idx in sorted(new_col['rows']):
                    rows_html.append(_calc_row(col, f'Row {idx}', 'added', '', new_col['rows'][idx]))
                continue

            if col not in new_tbl.columns:
                rows_html.append(_calc_row(col, 'Common', 'removed', old_col['common'], ''))
                for idx in sorted(old_col['rows']):
                    rows_html.append(_calc_row(col, f'Row {idx}', 'removed', old_col['rows'][idx], ''))
                continue

            if old_col['common'] != new_col['common']:
                rows_html.append(_calc_row(col, 'Common', 'modified', old_col['common'], new_col['common']))

            row_indices = set(old_col['rows']) | set(new_col['rows'])
            for idx in sorted(row_indices):
                o = old_col['rows'].get(idx, '')
                n = new_col['rows'].get(idx, '')
                if o == n:
                    continue
                if not o:
                    rows_html.append(_calc_row(col, f'Row {idx}', 'added', '', n))
                elif not n:
                    rows_html.append(_calc_row(col, f'Row {idx}', 'removed', o, ''))
                else:
                    rows_html.append(_calc_row(col, f'Row {idx}', 'modified', o, n))

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


def compare_lookup_tables(old: dict, new: dict) -> tuple[str, dict]:
    """Compare lookup tables"""
    added, removed, common = compare_dicts(old, new)
    stats = {'added': len(added), 'removed': len(removed), 'modified': 0, 'unchanged': 0}
    
    rows = []
    
    for name in sorted(added):
        rows.append(f'<tr class="added"><td>{escape(name)}</td><td><span class="badge badge-added">Added</span></td>'
                   f'<td>{len(new[name])} chars</td></tr>')
    
    for name in sorted(removed):
        rows.append(f'<tr class="removed"><td>{escape(name)}</td><td><span class="badge badge-removed">Removed</span></td>'
                   f'<td>{len(old[name])} chars</td></tr>')
    
    for name in sorted(common):
        if old[name] != new[name]:
            stats['modified'] += 1
            rows.append(f'<tr class="modified"><td>{escape(name)}</td><td><span class="badge badge-modified">Modified</span></td>'
                       f'<td>{len(new[name])} chars</td></tr>')
        else:
            stats['unchanged'] += 1
            rows.append(f'<tr class="unchanged"><td>{escape(name)}</td><td>—</td>'
                       f'<td>{len(old[name])} chars</td></tr>')
    
    html = f'''<table>
        <thead><tr><th>Table Name</th><th>Status</th><th>Size</th></tr></thead>
        <tbody>{"".join(rows) if rows else '<tr><td colspan="3" class="empty">No lookup tables found</td></tr>'}</tbody>
    </table>'''

    return html, stats


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


def _macro_task_rows(task_key: str, status: str, old_task, new_task, prop_changes=None) -> str:
    """Render one or more <tr> rows for a single macro task."""
    badge = f'<span class="badge badge-{status}">{status.title()}</span>'
    if status == 'added' or status == 'removed':
        t = new_task if status == 'added' else old_task
        n_props = len(t.properties)
        return (
            f'<tr class="{status}"><td>{escape(task_key)}</td><td>{badge}</td>'
            f'<td colspan="2">{n_props} properties</td></tr>'
        )
    # Modified case, emit one row per changed property
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
        rows.append(
            f'<tr class="{p_status}"><td>{task_cell}</td><td>{status_cell}</td>'
            f'<td>{escape(prop_name)} {p_badge}</td><td class="formula">{cell}</td></tr>'
        )
        first = False
    return ''.join(rows)
