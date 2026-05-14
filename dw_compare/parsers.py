"""
XML parsers for DriveWorks project files.
"""

import xml.etree.ElementTree as ET
from pathlib import Path

from .models import Variable, Constant, CalcTable, ComponentTask, DWProject


# Namespace mappings for DriveWorks XML
NS = {
    'project': 'http://schemas.driveworks.co.uk/project/',
    'comp-task': 'http://schemas.driveworks.co.uk/p-component-task/',
    'pcomp': 'http://schemas.driveworks.co.uk/p-component/',
    'meta': 'http://schemas.driveworks.co.uk/project-metadata/',
}


def parse_project_xml(path: Path) -> dict:
    """Parse project.xml for variables, calc tables, documents"""
    data = {'variables': {}, 'calc_tables': {}, 'documents': {}}
    
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return data
    
    # Parse Variables - try both namespaced (old) and attribute-based (TDM) formats
    for var in root.findall('.//project:Variable', NS):
        name = var.get('Name', '')
        formula = ""
        comment = ""
        
        formula_el = var.find('project:Formula', NS)
        if formula_el is not None and formula_el.text:
            formula = formula_el.text.strip()
        
        comment_el = var.find('project:Comment', NS)
        if comment_el is not None and comment_el.text:
            comment = comment_el.text.strip()
        
        if name:
            data['variables'][name] = Variable(name=name, formula=formula, comment=comment)
    
    # Also try non-namespaced Variable elements (TDM format)
    for var in root.findall('.//Variable'):
        display_name = var.get('DisplayName', '')
        store_name = var.get('StoreName', '')
        rule = var.get('Rule', '')
        comment = var.get('Comment', '')
        category = var.get('Category', '')
        
        if display_name:
            data['variables'][display_name] = Variable(
                name=display_name, store_name=store_name, 
                formula=rule, comment=comment, category=category
            )
    
    # Parse Calculation Tables
    for table in root.findall('.//project:CalculationTable', NS):
        tbl_name = table.get('Name', '')
        try:
            row_count = int(table.get('RowCount') or 0)
        except (TypeError, ValueError):
            row_count = 0
        
        columns = {}
        for col in table.findall('project:Columns/project:Column', NS):
            col_name = col.get('Name', '')
            col_data = {'common': '', 'rows': {}}
            
            # Common rule
            common = col.find('project:CommonRule/project:Formula', NS)
            if common is not None and common.text:
                col_data['common'] = common.text.strip()
            
            # Row-specific rules
            for rule in col.findall('project:Rules/project:Rule', NS):
                row_idx = rule.get('RowIndex')
                formula_el = rule.find('project:Formula', NS)
                if row_idx is not None and formula_el is not None:
                    col_data['rows'][int(row_idx)] = (formula_el.text or '').strip()
            
            columns[col_name] = col_data
        
        if tbl_name:
            data['calc_tables'][tbl_name] = CalcTable(name=tbl_name, row_count=row_count, columns=columns)
    
    # Parse Documents (Triggered Actions, etc.)
    for doc in root.findall('.//project:Document', NS):
        doc_name = doc.get('Name', '')
        doc_type = doc.get('Type', '')
        rules = {}
        
        for rule in doc.findall('.//project:Rule', NS):
            rule_id = rule.get('Id', '')
            formula_el = rule.find('project:Formula', NS)
            if rule_id and formula_el is not None:
                rules[rule_id] = (formula_el.text or '').strip()
        
        if doc_name:
            data['documents'][doc_name] = {'type': doc_type, 'rules': rules}
    
    return data


def parse_design_master(path: Path) -> dict:
    """Parse designMaster.xml (or TDM format) for constants, special vars, lookup tables, and variables"""
    data = {'constants': {}, 'special_vars': {}, 'lookup_tables': {}, 'variables': {}}
    
    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return data
    
    # Parse Constants - attribute-based format
    for const in root.findall('.//Constant'):
        display_name = const.get('DisplayName', '')
        store = const.get('StoreName', '')
        value = const.get('Value', '')
        comment = const.get('Comment', '')
        
        if display_name:
            data['constants'][display_name] = Constant(
                name=display_name, store_name=store, value=value, comment=comment
            )
    
    # Parse Special Variables - attribute-based format
    for sv in root.findall('.//SpecialVariable'):
        store = sv.get('StoreName', '')
        value = sv.get('Value', '')
        rule = sv.get('Rule', '')
        
        if store:
            data['special_vars'][store] = {'value': value, 'rule': rule}
    
    # Parse Variables from TDM format (attribute-based)
    for var in root.findall('.//Variable'):
        display_name = var.get('DisplayName', '')
        store_name = var.get('StoreName', '')
        rule = var.get('Rule', '')
        comment = var.get('Comment', '')
        category = var.get('Category', '')
        
        if display_name:
            data['variables'][display_name] = Variable(
                name=display_name, store_name=store_name,
                formula=rule, comment=comment, category=category
            )
    
    # Parse Lookup Tables
    for table in root.findall('.//Table'):
        name = table.get('Name', '')
        content = table.text or ''
        if name:
            data['lookup_tables'][name] = content.strip()
    
    return data


def _local_name(el: ET.Element) -> str:
    """Return element tag with any XML namespace stripped."""
    return el.tag.rsplit('}', 1)[-1]


def parse_component_tasks(path: Path) -> dict:
    """Parse componentTasks.xml"""
    tasks = {}

    try:
        tree = ET.parse(path)
        root = tree.getroot()
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return tasks

    for task in root.findall('.//comp-task:Task', NS):
        task_id = task.get('Id', '')
        name = task.get('Name', '')
        # .NET assembly-qualified type names look like "Ns.Sub.TypeName, AssemblyName".
        # Drop the assembly qualifier first, then take the final type name segment.
        raw_type = task.get('Type', '')
        type_only = raw_type.split(',', 1)[0].strip()
        task_type = type_only.rsplit('.', 1)[-1] if type_only else ''
        comp_id = task.get('ComponentId', '')
        scope = task.get('Scope', '')

        # Rules may live under any namespace inside the task — match by local name.
        rules = {}
        for rule in task.iter():
            if _local_name(rule) != 'Rule':
                continue
            rule_name = rule.get('Name', '')
            if not rule_name:
                continue
            formula_text = None
            for child in rule:
                if _local_name(child) == 'Formula':
                    formula_text = (child.text or '').strip()
                    break
            if formula_text is not None:
                rules[rule_name] = formula_text

        key = f"{name}|{comp_id or scope or task_id}"
        tasks[key] = ComponentTask(
            id=task_id, name=name, task_type=task_type,
            component_id=comp_id, scope=scope, rules=rules
        )

    return tasks


def load_project(folder: Path) -> DWProject:
    """Load all DriveWorks project files from a folder (recursively)"""
    proj = DWProject()
    
    # Recursively find all project.xml files
    for proj_file in folder.rglob('project.xml'):
        print(f"  Found: {proj_file}")
        data = parse_project_xml(proj_file)
        proj.variables.update(data['variables'])
        proj.calc_tables.update(data['calc_tables'])
        proj.documents.update(data['documents'])
    
    # Recursively find all designMaster.xml files
    for dm_file in folder.rglob('designMaster.xml'):
        print(f"  Found: {dm_file}")
        data = parse_design_master(dm_file)
        proj.constants.update(data['constants'])
        proj.special_vars.update(data['special_vars'])
        proj.lookup_tables.update(data['lookup_tables'])
        proj.variables.update(data.get('variables', {}))
    
    # Recursively find all TDM files
    for tdm_file in folder.rglob('*.tdm'):
        print(f"  Found: {tdm_file}")
        data = parse_design_master(tdm_file)
        proj.constants.update(data['constants'])
        proj.special_vars.update(data['special_vars'])
        proj.lookup_tables.update(data['lookup_tables'])
        proj.variables.update(data.get('variables', {}))
    
    # Recursively find all componentTasks.xml files
    for ct_file in folder.rglob('componentTasks.xml'):
        print(f"  Found: {ct_file}")
        proj.component_tasks.update(parse_component_tasks(ct_file))
    
    return proj
