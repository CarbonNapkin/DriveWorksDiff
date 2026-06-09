"""
HTML report generation for DriveWorks comparison.
"""

from datetime import datetime
from html import escape

from ._version import __version__, __url__
from .models import DWProject
from .comparers import (
    compare_variables,
    compare_constants,
    compare_special_vars,
    compare_calc_tables,
    compare_component_tasks,
    compare_documents,
    compare_lookup_tables,
    compare_data_tables,
    compare_nav_steps,
    compare_spec_macros,
    compare_forms,
)


def generate_html_report(old_proj: DWProject, new_proj: DWProject, 
                         old_name: str, new_name: str) -> str:
    """Generate comprehensive HTML comparison report"""
    
    sections = []
    summary = {'added': 0, 'removed': 0, 'modified': 0, 'unchanged': 0}
    
    # --- Variables Section ---
    var_html, var_stats = compare_variables(old_proj.variables, new_proj.variables)
    sections.append(('Variables', var_html, var_stats))
    
    # --- Constants Section ---
    const_html, const_stats = compare_constants(old_proj.constants, new_proj.constants)
    sections.append(('Constants', const_html, const_stats))
    
    # --- Special Variables Section ---
    sv_html, sv_stats = compare_special_vars(old_proj.special_vars, new_proj.special_vars)
    sections.append(('Special Variables', sv_html, sv_stats))
    
    # --- Calculation Tables Section ---
    ct_html, ct_stats = compare_calc_tables(old_proj.calc_tables, new_proj.calc_tables)
    sections.append(('Calculation Tables', ct_html, ct_stats))
    
    # --- Component Tasks Section ---
    task_html, task_stats = compare_component_tasks(old_proj.component_tasks, new_proj.component_tasks)
    sections.append(('Component Tasks', task_html, task_stats))
    
    # --- Documents Section ---
    doc_html, doc_stats = compare_documents(old_proj.documents, new_proj.documents)
    sections.append(('Documents', doc_html, doc_stats))
    
    # --- Lookup Tables Section ---
    lt_html, lt_stats = compare_lookup_tables(old_proj.lookup_tables, new_proj.lookup_tables)
    sections.append(('Lookup Tables', lt_html, lt_stats))

    # --- Data Tables Section ---
    dt_html, dt_stats = compare_data_tables(old_proj.data_tables, new_proj.data_tables)
    sections.append(('Data Tables', dt_html, dt_stats))

    # --- Specification Macros Section ---
    macro_html, macro_stats = compare_spec_macros(old_proj.spec_macros, new_proj.spec_macros)
    sections.append(('Specification Macros', macro_html, macro_stats))

    # --- Navigation Steps Section ---
    nav_html, nav_stats = compare_nav_steps(old_proj.nav_steps, new_proj.nav_steps)
    sections.append(('Navigation Steps', nav_html, nav_stats))

    # --- Forms Section ---
    form_html, form_stats = compare_forms(old_proj.forms, new_proj.forms)
    sections.append(('Forms', form_html, form_stats))
    
    # Aggregate summary
    for _, _, stats in sections:
        summary['added'] += stats['added']
        summary['removed'] += stats['removed']
        summary['modified'] += stats['modified']
        summary['unchanged'] += stats['unchanged']
    
    # Build full HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DriveWorks Project Comparison</title>
    <style>
        :root {{
            --added-bg: #e6ffec;
            --added-bg-strong: #c8f0d3;
            --added-border: #2e9b40;
            --removed-bg: #ffebe9;
            --removed-bg-strong: #f7c8c4;
            --removed-border: #d33b30;
            --modified-bg: #fff8e1;
            --modified-bg-strong: #ffe9a8;
            --modified-border: #e6890c;
            --unchanged-bg: #f5f5f5;
            --rule-bg: #f7f8fa;
            --header-stack: 44px;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.4;
            max-width: 1400px;
            margin: 0 auto;
            padding: 14px 16px 32px;
            background: #fafafa;
            color: #1f2024;
        }}

        h1 {{
            color: #1a237e;
            border-bottom: 2px solid #3f51b5;
            padding-bottom: 6px;
            font-size: 22px;
            margin: 0 0 8px;
        }}

        .meta {{
            color: #555;
            font-size: 13px;
            margin: 0 0 10px;
        }}

        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 10px;
            margin: 10px 0 12px;
        }}

        .stat-card {{
            padding: 8px 12px;
            border-radius: 6px;
            font-weight: 600;
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            font-size: 13px;
        }}
        .stat-card .stat-num {{ font-size: 20px; font-weight: 700; }}

        .stat-added {{ background: var(--added-bg); border-left: 4px solid var(--added-border); }}
        .stat-removed {{ background: var(--removed-bg); border-left: 4px solid var(--removed-border); }}
        .stat-modified {{ background: var(--modified-bg); border-left: 4px solid var(--modified-border); }}
        .stat-unchanged {{ background: var(--unchanged-bg); border-left: 4px solid #9e9e9e; }}

        /* Filter bar sticks at top of viewport while scrolling. */
        .filter-bar {{
            position: sticky;
            top: 0;
            z-index: 10;
            margin: 0 0 14px;
            padding: 8px 10px;
            background: rgba(255,255,255,0.92);
            backdrop-filter: saturate(180%) blur(8px);
            border: 1px solid #e3e5e9;
            border-radius: 8px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        .filter-bar label {{ cursor: pointer; font-size: 13px; }}
        .filter-bar button {{
            padding: 4px 10px;
            font-size: 13px;
            cursor: pointer;
            border: 1px solid #c8ccd2;
            background: #fff;
            border-radius: 6px;
        }}
        .filter-bar button:hover {{ background: #f0f1f4; }}

        #searchBox {{
            flex: 1 0 220px;
            min-width: 220px;
            padding: 5px 10px;
            border: 1px solid #c8ccd2;
            border-radius: 6px;
            font-size: 13px;
        }}
        #searchBox:focus {{
            outline: 2px solid #3f51b5;
            border-color: #3f51b5;
        }}

        .section {{
            background: white;
            border-radius: 8px;
            margin: 10px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            overflow: hidden;
        }}

        /* Sections with no changes hide entirely by default; toggle restores them. */
        body.hide-quiet .section[data-quiet="1"] {{ display: none; }}

        .section-header {{
            background: #3f51b5;
            color: white;
            padding: 8px 14px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 14px;
        }}
        .section-header:hover {{ background: #303f9f; }}
        .section-header .title {{ font-weight: 600; }}

        .section-content {{
            padding: 0;
            max-height: min(78vh, 780px);
            overflow-y: auto;
        }}
        .section.collapsed .section-content {{ display: none; }}

        /* Sticky per-group sub-headers (used by Forms, Macros, Calc Tables, etc.). */
        .section-content > h3 {{
            position: sticky;
            top: 0;
            z-index: 3;
            margin: 0;
            padding: 8px 14px;
            font-size: 14px;
            background: #fafbfd;
            border-top: 1px solid #e6e8ec;
            border-bottom: 1px solid #e6e8ec;
            box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }}
        .section-content > h3:first-child {{ border-top: none; }}
        .section-content > h3.added {{ background: var(--added-bg); }}
        .section-content > h3.removed {{ background: var(--removed-bg); }}
        .section-content > h3.modified {{ background: var(--modified-bg); }}
        .section-content > h3 small {{ color: #555; font-weight: 500; margin-left: 6px; }}

        .section-content > p.empty {{ padding: 12px 14px; margin: 0; }}

        .badge {{
            display: inline-block;
            padding: 1px 8px;
            border-radius: 10px;
            font-size: 11px;
            margin-left: 6px;
            vertical-align: middle;
            white-space: nowrap;
        }}
        .badge-added {{ background: var(--added-border); color: white; }}
        .badge-removed {{ background: var(--removed-border); color: white; }}
        .badge-modified {{ background: var(--modified-border); color: white; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}

        th, td {{
            padding: 5px 10px;
            text-align: left;
            border-bottom: 1px solid #ececef;
            vertical-align: top;
        }}
        td:first-child {{ word-break: break-word; }}

        /* Table column header sticks just under any sticky h3. */
        th {{
            background: #f0f2f5;
            font-weight: 600;
            position: sticky;
            top: var(--header-stack);
            z-index: 2;
            box-shadow: inset 0 -1px 0 #d8dbe0;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            color: #495160;
        }}
        /* When no h3 sub-header is present in a section, th sits at top: 0. */
        .section-content > table:first-child th,
        .section-content > table:only-child th {{ top: 0; }}

        tbody tr:hover {{ background: #eef1f5; }}
        tr.added {{ background: var(--added-bg); }}
        tr.added:hover {{ background: var(--added-bg-strong); }}
        tr.removed {{ background: var(--removed-bg); }}
        tr.removed:hover {{ background: var(--removed-bg-strong); }}
        tr.modified {{ background: var(--modified-bg); }}
        tr.modified:hover {{ background: var(--modified-bg-strong); }}

        /* Group-start marks the first row of a parent-child group (Form ->
           Control -> Property, Macro -> Task -> Property, CalcTable Column
           -> Scope). Repeated cells are blank on later rows, so this border
           draws the visible parent boundary. */
        tbody tr.group-start td {{ border-top: 2px solid #b8bcc4; }}
        tbody tr.group-start:first-child td {{ border-top: none; }}
        /* The first one or two cells of a row are identity cells; on later
           rows in a group they are blank. Give them slightly muted styling so
           the eye reads the grouped chunk as one block. */
        td.grouper {{ font-weight: 500; color: #2a2c30; background: rgba(0,0,0,0.015); }}
        tr.added td.grouper, tr.removed td.grouper, tr.modified td.grouper {{
            background: rgba(0,0,0,0.04);
        }}

        /* Lookup-table grids render the actual CSV data with per-cell
           highlighting. Unchanged rows are hidden by default; the
           "Show unchanged lookup rows" filter brings them back. */
        table.lookup-grid {{ table-layout: auto; }}
        table.lookup-grid th {{
            top: var(--header-stack);
            white-space: nowrap;
        }}
        table.lookup-grid th.col-added {{ background: var(--added-bg); }}
        table.lookup-grid th.col-removed {{ background: var(--removed-bg); }}
        table.lookup-grid td {{
            font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace;
            font-size: 12px;
            max-width: 320px;
            overflow-wrap: anywhere;
        }}
        table.lookup-grid td.cell-changed {{
            background: var(--modified-bg-strong);
            font-weight: 500;
        }}
        table.lookup-grid td.cell-added {{ background: var(--added-bg-strong); }}
        table.lookup-grid td.cell-removed {{ background: var(--removed-bg-strong); }}
        body:not(.show-lookup-unchanged) table.lookup-grid tbody tr.unchanged {{ display: none; }}

        .formula {{
            font-family: 'JetBrains Mono', 'SF Mono', Menlo, Consolas, monospace;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-word;
            background: var(--rule-bg);
            padding: 3px 7px;
            border-radius: 4px;
            max-width: min(60vw, 720px);
            line-height: 1.35;
        }}

        span.added {{
            background: #b6e8c1;
            padding: 0 3px;
            border-radius: 3px;
        }}
        span.removed {{
            background: #f6c1c1;
            padding: 0 3px;
            border-radius: 3px;
            text-decoration: line-through;
        }}

        .empty {{ color: #888; font-style: italic; }}
        .toggle {{ font-size: 18px; user-select: none; }}
    </style>
</head>
<body>
    <h1>🔄 DriveWorks Project Comparison</h1>
    
    <div class="meta">
        <strong>Old:</strong> <span id="oldName">{escape(old_name)}</span> &nbsp;→&nbsp; <strong>New:</strong> <span id="newName">{escape(new_name)}</span><br>
        Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by
        <a href="{__url__}" style="color:#3f51b5;text-decoration:none;">DriveWorks Project Compare v{__version__}</a>
    </div>
    
    <div class="summary">
        <div class="stat-card stat-added"><span>➕ Added</span><span class="stat-num">{summary['added']}</span></div>
        <div class="stat-card stat-removed"><span>➖ Removed</span><span class="stat-num">{summary['removed']}</span></div>
        <div class="stat-card stat-modified"><span>✏️ Modified</span><span class="stat-num">{summary['modified']}</span></div>
        <div class="stat-card stat-unchanged"><span>✓ Unchanged</span><span class="stat-num">{summary['unchanged']}</span></div>
    </div>

    <div class="filter-bar">
        <input type="text" id="searchBox" placeholder="🔍 Search names, formulas..." oninput="filterRows()">
        <button id="flipBtn" onclick="flipDirection()">🔄 Flip Direction</button>
        <label><input type="checkbox" id="showAdded" checked onchange="filterRows()"> Added</label>
        <label><input type="checkbox" id="showRemoved" checked onchange="filterRows()"> Removed</label>
        <label><input type="checkbox" id="showModified" checked onchange="filterRows()"> Modified</label>
        <label><input type="checkbox" id="showUnchanged" onchange="filterRows()"> Unchanged rows</label>
        <label><input type="checkbox" id="showQuietSections" onchange="applySectionVisibility()"> Show unchanged sections</label>
        <label><input type="checkbox" id="showLookupUnchanged" onchange="applyLookupRowVisibility()"> Show unchanged lookup rows</label>
        <button onclick="expandAll(true)">Expand all</button>
        <button onclick="expandAll(false)">Collapse all</button>
    </div>
'''
    
    for section_name, section_content, stats in sections:
        badges = ''
        if stats['added']: badges += f'<span class="badge badge-added">+{stats["added"]}</span>'
        if stats['removed']: badges += f'<span class="badge badge-removed">-{stats["removed"]}</span>'
        if stats['modified']: badges += f'<span class="badge badge-modified">~{stats["modified"]}</span>'

        quiet = stats['added'] + stats['removed'] + stats['modified'] == 0
        collapsed = 'collapsed' if quiet else ''
        unchanged_count = stats.get('unchanged', 0)
        if quiet and unchanged_count:
            badges += f'<span class="badge" style="background:#dadde2;color:#3b3f48">{unchanged_count} unchanged</span>'

        html += f'''
    <div class="section {collapsed}" data-quiet="{1 if quiet else 0}">
        <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
            <span class="title">{section_name}{badges}</span>
            <span class="toggle">▼</span>
        </div>
        <div class="section-content">
            {section_content}
        </div>
    </div>
'''
    
    html += '''
    <script>
        let flipped = false;
        
        function flipDirection() {
            flipped = !flipped;
            
            // Swap old/new names
            const oldName = document.getElementById('oldName');
            const newName = document.getElementById('newName');
            const temp = oldName.textContent;
            oldName.textContent = newName.textContent;
            newName.textContent = temp;
            
            // Swap added/removed classes on rows
            document.querySelectorAll('tr.added, tr.removed').forEach(row => {
                if (row.classList.contains('added')) {
                    row.classList.remove('added');
                    row.classList.add('removed');
                } else {
                    row.classList.remove('removed');
                    row.classList.add('added');
                }
            });
            
            // Swap badge text
            document.querySelectorAll('.badge-added, .badge-removed').forEach(badge => {
                if (badge.classList.contains('badge-added')) {
                    badge.classList.remove('badge-added');
                    badge.classList.add('badge-removed');
                    badge.textContent = badge.textContent.replace('Added', 'Removed').replace('New', 'Old').replace('+', '-');
                } else {
                    badge.classList.remove('badge-removed');
                    badge.classList.add('badge-added');
                    badge.textContent = badge.textContent.replace('Removed', 'Added').replace('Old', 'New').replace('-', '+');
                }
            });
            
            // Swap inline diff spans
            document.querySelectorAll('span.added, span.removed').forEach(span => {
                if (span.classList.contains('added')) {
                    span.classList.remove('added');
                    span.classList.add('removed');
                } else {
                    span.classList.remove('removed');
                    span.classList.add('added');
                }
            });

            // Swap lookup-grid per-cell and per-column highlight classes.
            document.querySelectorAll('.cell-added, .cell-removed, .col-added, .col-removed').forEach(el => {
                if (el.classList.contains('cell-added')) el.classList.replace('cell-added', 'cell-removed');
                else if (el.classList.contains('cell-removed')) el.classList.replace('cell-removed', 'cell-added');
                if (el.classList.contains('col-added')) el.classList.replace('col-added', 'col-removed');
                else if (el.classList.contains('col-removed')) el.classList.replace('col-removed', 'col-added');
            });
            
            // Swap the Added/Removed COUNTS only (labels and colors stay put).
            const addedNum = document.querySelector('.stat-added .stat-num');
            const removedNum = document.querySelector('.stat-removed .stat-num');
            const tempVal = addedNum.textContent;
            addedNum.textContent = removedNum.textContent;
            removedNum.textContent = tempVal;
            
            // Update button text
            document.getElementById('flipBtn').textContent = flipped ? '🔄 Flip Back' : '🔄 Flip Direction';
            
            filterRows();
        }
        
        function filterRows() {
            const showAdded = document.getElementById('showAdded').checked;
            const showRemoved = document.getElementById('showRemoved').checked;
            const showModified = document.getElementById('showModified').checked;
            const showUnchanged = document.getElementById('showUnchanged').checked;
            const searchText = document.getElementById('searchBox').value.toLowerCase().trim();
            
            document.querySelectorAll('tbody tr').forEach(row => {
                // Skip empty placeholder rows
                if (row.querySelector('.empty')) return;
                
                // Check status filter
                let statusMatch = false;
                if (row.classList.contains('added') && showAdded) statusMatch = true;
                else if (row.classList.contains('removed') && showRemoved) statusMatch = true;
                else if (row.classList.contains('modified') && showModified) statusMatch = true;
                else if (row.classList.contains('unchanged') && showUnchanged) statusMatch = true;
                
                // Check search filter
                let searchMatch = true;
                if (searchText) {
                    const rowText = row.textContent.toLowerCase();
                    searchMatch = rowText.includes(searchText);
                }
                
                row.style.display = (statusMatch && searchMatch) ? '' : 'none';
            });
            
            // Keep a group's identity row visible whenever any row in that
            // group is still visible, so filtered child rows are not orphaned.
            document.querySelectorAll('.section-content tbody').forEach(tb => {
                const rows = Array.from(tb.rows);
                let i = 0;
                while (i < rows.length) {
                    if (!rows[i].classList.contains('group-start')) { i++; continue; }
                    let j = i + 1;
                    let anyVisible = rows[i].style.display !== 'none';
                    while (j < rows.length && !rows[j].classList.contains('group-start')) {
                        if (rows[j].style.display !== 'none') anyVisible = true;
                        j++;
                    }
                    if (anyVisible) rows[i].style.display = '';
                    i = j;
                }
            });

            // Also filter h3 headers (added/removed/modified calc tables have no row body)
            document.querySelectorAll('.section-content h3').forEach(h3 => {
                let headerStatus = null;
                if (h3.classList.contains('added')) headerStatus = 'added';
                else if (h3.classList.contains('removed')) headerStatus = 'removed';
                else if (h3.classList.contains('modified')) headerStatus = 'modified';

                let statusMatch = true;
                if (headerStatus === 'added') statusMatch = showAdded;
                else if (headerStatus === 'removed') statusMatch = showRemoved;
                else if (headerStatus === 'modified') statusMatch = showModified;

                const headerText = h3.textContent.toLowerCase();
                const searchMatch = !searchText || headerText.includes(searchText);
                const show = statusMatch && searchMatch;

                h3.style.display = show ? '' : 'none';
                const table = h3.nextElementSibling;
                if (table && table.tagName === 'TABLE') table.style.display = show ? '' : 'none';
            });
        }

        function applySectionVisibility() {
            const show = document.getElementById('showQuietSections').checked;
            document.body.classList.toggle('hide-quiet', !show);
        }

        function applyLookupRowVisibility() {
            const show = document.getElementById('showLookupUnchanged').checked;
            document.body.classList.toggle('show-lookup-unchanged', show);
        }

        function expandAll(open) {
            document.querySelectorAll('.section').forEach(s => {
                if (open) s.classList.remove('collapsed');
                else s.classList.add('collapsed');
            });
        }

        // Default: hide sections with no changes; user can toggle them back on.
        applySectionVisibility();
        applyLookupRowVisibility();
        filterRows();
    </script>
    <footer style="margin-top:24px;padding-top:12px;border-top:1px solid #e3e5e9;color:#888;font-size:12px;text-align:center;">
        DriveWorks Project Compare v''' + __version__ + ''' &middot;
        <a href="''' + __url__ + '''" style="color:#888;">''' + __url__ + '''</a>
    </footer>
</body>
</html>
'''
    return html
