"""
HTML report generation for DriveWorks comparison.
"""

from datetime import datetime
from html import escape

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
            --added-border: #4caf50;
            --removed-bg: #ffebe9;
            --removed-border: #f44336;
            --modified-bg: #fff8e1;
            --modified-border: #ff9800;
            --unchanged-bg: #f5f5f5;
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }}
        
        h1 {{ color: #1a237e; border-bottom: 3px solid #3f51b5; padding-bottom: 10px; }}
        h2 {{ color: #283593; margin-top: 30px; }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
        }}
        
        .stat-added {{ background: var(--added-bg); border-left: 4px solid var(--added-border); }}
        .stat-removed {{ background: var(--removed-bg); border-left: 4px solid var(--removed-border); }}
        .stat-modified {{ background: var(--modified-bg); border-left: 4px solid var(--modified-border); }}
        .stat-unchanged {{ background: var(--unchanged-bg); border-left: 4px solid #9e9e9e; }}
        
        .section {{
            background: white;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .section-header {{
            background: #3f51b5;
            color: white;
            padding: 12px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .section-header:hover {{ background: #303f9f; }}
        
        .section-content {{
            padding: 20px;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .section.collapsed .section-content {{ display: none; }}
        
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
        }}
        
        .badge-added {{ background: var(--added-border); color: white; }}
        .badge-removed {{ background: var(--removed-border); color: white; }}
        .badge-modified {{ background: var(--modified-border); color: white; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}
        
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{ background: #f5f5f5; font-weight: 600; position: sticky; top: 0; }}
        
        tr.added {{ background: var(--added-bg); }}
        tr.removed {{ background: var(--removed-bg); }}
        tr.modified {{ background: var(--modified-bg); }}
        
        .formula {{
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-break: break-all;
            background: #f8f8f8;
            padding: 4px 8px;
            border-radius: 4px;
            max-width: 600px;
        }}
        
        span.added {{
            background: #acf2bd;
            padding: 1px 3px;
            border-radius: 3px;
        }}
        
        span.removed {{
            background: #fdb8c0;
            padding: 1px 3px;
            border-radius: 3px;
            text-decoration: line-through;
        }}
        
        .meta {{
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        .empty {{ color: #999; font-style: italic; }}
        
        .toggle {{ font-size: 20px; }}
        
        .filter-bar {{
            margin: 10px 0;
            padding: 12px;
            background: #f0f0f0;
            border-radius: 4px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 10px;
        }}
        
        .filter-bar label {{ margin-right: 10px; cursor: pointer; }}
        
        #searchBox {{
            flex-shrink: 0;
        }}
        
        #searchBox:focus {{
            outline: 2px solid #3f51b5;
            border-color: #3f51b5;
        }}
    </style>
</head>
<body>
    <h1>🔄 DriveWorks Project Comparison</h1>
    
    <div class="meta">
        <strong>Old:</strong> <span id="oldName">{escape(old_name)}</span> &nbsp;→&nbsp; <strong>New:</strong> <span id="newName">{escape(new_name)}</span><br>
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
    
    <div class="summary">
        <div class="stat-card stat-added">➕ Added<br><span style="font-size: 24px">{summary['added']}</span></div>
        <div class="stat-card stat-removed">➖ Removed<br><span style="font-size: 24px">{summary['removed']}</span></div>
        <div class="stat-card stat-modified">✏️ Modified<br><span style="font-size: 24px">{summary['modified']}</span></div>
        <div class="stat-card stat-unchanged">✓ Unchanged<br><span style="font-size: 24px">{summary['unchanged']}</span></div>
    </div>
    
    <div class="filter-bar">
        <input type="text" id="searchBox" placeholder="🔍 Search variables, formulas..." 
               oninput="filterRows()" style="padding: 6px 12px; width: 300px; margin-right: 20px; border: 1px solid #ccc; border-radius: 4px;">
        <button id="flipBtn" onclick="flipDirection()" style="padding: 6px 12px; margin-right: 20px; cursor: pointer; font-weight: bold;">🔄 Flip Direction</button>
        <label><input type="checkbox" id="showAdded" checked onchange="filterRows()"> Show Added</label>
        <label><input type="checkbox" id="showRemoved" checked onchange="filterRows()"> Show Removed</label>
        <label><input type="checkbox" id="showModified" checked onchange="filterRows()"> Show Modified</label>
        <label><input type="checkbox" id="showUnchanged" onchange="filterRows()"> Show Unchanged</label>
    </div>
'''
    
    for section_name, section_content, stats in sections:
        badges = ''
        if stats['added']: badges += f'<span class="badge badge-added">+{stats["added"]}</span>'
        if stats['removed']: badges += f'<span class="badge badge-removed">-{stats["removed"]}</span>'
        if stats['modified']: badges += f'<span class="badge badge-modified">~{stats["modified"]}</span>'
        
        collapsed = 'collapsed' if stats['added'] + stats['removed'] + stats['modified'] == 0 else ''
        
        html += f'''
    <div class="section {collapsed}">
        <div class="section-header" onclick="this.parentElement.classList.toggle('collapsed')">
            <span>{section_name} {badges}</span>
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
                    badge.textContent = badge.textContent.replace('Added', 'Removed').replace('+', '-');
                } else {
                    badge.classList.remove('badge-removed');
                    badge.classList.add('badge-added');
                    badge.textContent = badge.textContent.replace('Removed', 'Added').replace('-', '+');
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
            
            // Swap summary card values
            const addedCard = document.querySelector('.stat-added span');
            const removedCard = document.querySelector('.stat-removed span');
            const tempVal = addedCard.textContent;
            addedCard.textContent = removedCard.textContent;
            removedCard.textContent = tempVal;
            
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
        filterRows();
    </script>
</body>
</html>
'''
    return html
