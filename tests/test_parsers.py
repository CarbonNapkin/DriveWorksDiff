"""Tests for the XML parsers: a small project parses into the expected models,
and malformed input degrades gracefully instead of crashing."""

import xml.etree.ElementTree as ET

from dw_compare.parsers import (
    parse_project_xml, parse_design_master, parse_component_tasks, load_project,
    _read_form_property,
)

PROJECT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<p:Project xmlns:p="http://schemas.driveworks.co.uk/project/">
  <p:Variables>
    <p:Variable Name="W"><p:Formula>=600</p:Formula><p:Comment>width</p:Comment></p:Variable>
  </p:Variables>
  <p:CalculationTables>
    <p:CalculationTable Name="T" RowCount="2">
      <p:Columns><p:Column Name="C">
        <p:CommonRule><p:Formula>=1</p:Formula></p:CommonRule>
        <p:Rules>
          <p:Rule RowIndex="0"><p:Formula>=A</p:Formula></p:Rule>
          <p:Rule RowIndex="bad"><p:Formula>=skip</p:Formula></p:Rule>
        </p:Rules>
      </p:Column></p:Columns>
    </p:CalculationTable>
  </p:CalculationTables>
  <p:Documents>
    <p:Document Name="D" Type="DriveWorks.PrintDocument, DriveWorks.Engine">
      <p:Rules><p:Rule Id="r1"><p:Formula>=1</p:Formula></p:Rule></p:Rules>
    </p:Document>
  </p:Documents>
  <p:Forms><Form Name="MainForm"><Controls>
    <ComboBox Name="Sel"><VisibleRule IsStatic="False"><Rule>=True</Rule></VisibleRule></ComboBox>
  </Controls></Form></p:Forms>
</p:Project>'''

DESIGN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<DesignMaster>
  <Constants><Constant DisplayName="M" StoreName="M" Value="2" Comment="c"/></Constants>
  <SpecialVariables><SpecialVariable StoreName="R" Value="" Rule='="A"'/></SpecialVariables>
  <Tables><Table Name="L">Material,Cost
Steel,2.5</Table></Tables>
  <Navigation><Step Name="Start" Type="Form" NextStepRule="=True" NextStepValue="Opt"/></Navigation>
</DesignMaster>'''

CT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<ct:ComponentTasks xmlns:ct="http://schemas.driveworks.co.uk/p-component-task/">
  <ct:Task Id="t1" Name="Gen" Type="DriveWorks.Draw, DriveWorks.Engine" ComponentId="c1">
    <ct:Rules><ct:Rule Name="Tmpl"><ct:Formula>="A3"</ct:Formula></ct:Rule></ct:Rules>
  </ct:Task>
</ct:ComponentTasks>'''


def test_parse_project_xml(tmp_path):
    p = tmp_path / "project.xml"
    p.write_text(PROJECT_XML, encoding="utf-8")
    data = parse_project_xml(p)
    assert data["variables"]["W"].formula == "=600"
    assert data["variables"]["W"].comment == "width"
    assert "T" in data["calc_tables"]
    assert data["documents"]["D"]["type"] == "PrintDocument"
    assert "MainForm" in data["forms"]
    assert "Sel" in data["forms"]["MainForm"].controls


def test_malformed_rowindex_skipped_not_crash(tmp_path):  # REGRESSION (unguarded int())
    p = tmp_path / "project.xml"
    p.write_text(PROJECT_XML, encoding="utf-8")
    rows = parse_project_xml(p)["calc_tables"]["T"].columns["C"]["rows"]
    assert rows.get(0) == "=A"   # the valid row is parsed
    assert "bad" not in rows     # the non-numeric RowIndex is skipped, no crash


def test_parse_design_master(tmp_path):
    p = tmp_path / "designMaster.xml"
    p.write_text(DESIGN_XML, encoding="utf-8")
    data = parse_design_master(p)
    assert data["constants"]["M"].value == "2"
    assert "L" in data["lookup_tables"]
    assert "Start" in data["nav_steps"]
    assert "special_vars" not in data  # Special Variables are no longer parsed


def test_parse_component_tasks(tmp_path):
    p = tmp_path / "componentTasks.xml"
    p.write_text(CT_XML, encoding="utf-8")
    tasks = parse_component_tasks(p)
    assert len(tasks) == 1
    task = next(iter(tasks.values()))
    assert task.name == "Gen"
    assert task.rules["Tmpl"] == '="A3"'


def test_load_project_warns_on_multiple_specs(tmp_path, capsys):
    # Two nested specifications get merged into one flat view; load_project
    # should surface that rather than merging silently.
    for sub in ("specA", "specB"):
        d = tmp_path / sub
        d.mkdir()
        (d / "project.xml").write_text(PROJECT_XML, encoding="utf-8")
    load_project(tmp_path)
    assert "Multiple specifications" in capsys.readouterr().out


def test_load_project_end_to_end(tmp_path):
    (tmp_path / "project.xml").write_text(PROJECT_XML, encoding="utf-8")
    (tmp_path / "designMaster.xml").write_text(DESIGN_XML, encoding="utf-8")
    (tmp_path / "componentTasks.xml").write_text(CT_XML, encoding="utf-8")
    proj = load_project(tmp_path)
    assert "W" in proj.variables
    assert "M" in proj.constants
    assert proj.component_tasks


# --- TDM designMaster + category resolution: the format ~100% of real projects
# actually use (variables/categories live in the attribute-based designMaster,
# category GUIDs resolve against project.xml). Validated on real data; locked in
# here with synthetic fixtures so it stays covered in CI. ---

CATS_PROJECT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<p:Project xmlns:p="http://schemas.driveworks.co.uk/project/">
  <p:Categories>
    <p:Category UniqueId="cat-guid-1" Name="Dimensions"/>
  </p:Categories>
</p:Project>'''

TDM_DESIGN_XML = '''<?xml version="1.0" encoding="utf-8"?>
<TDM>
  <Variable DisplayName="Width" StoreName="DWVariableWidth" Rule="=Length+5" Category="cat-guid-1" Comment="w"/>
  <Variable DisplayName="Depth" StoreName="DWVariableDepth" Rule="=10" Category="unknown-guid"/>
</TDM>'''


def test_tdm_designmaster_variable_parsing(tmp_path):
    p = tmp_path / "designMaster.xml"
    p.write_text(TDM_DESIGN_XML, encoding="utf-8")
    v = parse_design_master(p)["variables"]["Width"]
    assert v.formula == "=Length+5"           # TDM stores the rule in the Rule attribute
    assert v.store_name == "DWVariableWidth"
    assert v.category == "cat-guid-1"          # raw GUID at parse time
    assert v.comment == "w"


def test_load_project_resolves_category_guids(tmp_path):
    (tmp_path / "project.xml").write_text(CATS_PROJECT_XML, encoding="utf-8")
    (tmp_path / "designMaster.xml").write_text(TDM_DESIGN_XML, encoding="utf-8")
    proj = load_project(tmp_path)
    assert proj.variables["Width"].category == "Dimensions"     # GUID resolved to its name
    assert proj.variables["Depth"].category == "unknown-guid"   # unmatched GUID left as-is


MACRO_PROJECT_XML = '''<?xml version="1.0" encoding="utf-8"?>
<p:Project xmlns:p="http://schemas.driveworks.co.uk/project/">
  <p:SpecificationMacros>
    <p:SpecificationMacro Name="GoToForm">
      <Tasks>
        <Task Title="Skip to Form" Type="DriveWorks.SkipToFormTask, DriveWorks.Engine">
          <Properties>
            <Property Name="FormName"><Binding><Formula>="MainForm"</Formula></Binding></Property>
            <Property Name="Condition"><Binding><Formula>=True</Formula></Binding></Property>
          </Properties>
        </Task>
      </Tasks>
    </p:SpecificationMacro>
  </p:SpecificationMacros>
</p:Project>'''


def test_spec_macro_property_binding_formula_parsing(tmp_path):
    p = tmp_path / "project.xml"
    p.write_text(MACRO_PROJECT_XML, encoding="utf-8")
    m = parse_project_xml(p)["spec_macros"]["GoToForm"]
    assert len(m.tasks) == 1
    t = m.tasks[0]
    assert t.title == "Skip to Form"
    assert t.task_type == "SkipToFormTask"          # .NET assembly qualifier stripped
    assert t.properties["FormName"] == '="MainForm"'  # nested Property->Binding->Formula
    assert t.properties["Condition"] == "=True"


# --- Form property shapes. Real data has rule-driven props that store only a
# cached <Value> (no <Rule>) under IsStatic="False", and the parser must let a
# <Rule> win when both are present. ---

def test_read_form_property_cached_value_under_nonstatic():
    el = ET.fromstring('<Visible IsStatic="False"><Value>True</Value></Visible>')
    assert _read_form_property(el) == (False, "True")

def test_read_form_property_rule_wins_over_value():
    el = ET.fromstring('<Items IsStatic="False"><Value>cached</Value><Rule>=Length&gt;5</Rule></Items>')
    assert _read_form_property(el) == (False, "=Length>5")

def test_read_form_property_defaults_to_static():
    el = ET.fromstring('<Caption><Value>Width</Value></Caption>')  # no IsStatic attr
    assert _read_form_property(el) == (True, "Width")


def test_load_project_discovers_files_in_nested_subfolder(tmp_path):
    # Run-specification layout: the project files live under a nested
    # ".../<spec>/DriveWorksFiles/" folder, which load_project finds via rglob.
    spec = tmp_path / "Order 0042" / "DriveWorksFiles"
    spec.mkdir(parents=True)
    (spec / "project.xml").write_text(MACRO_PROJECT_XML, encoding="utf-8")
    (spec / "designMaster.xml").write_text(TDM_DESIGN_XML, encoding="utf-8")
    proj = load_project(tmp_path)
    assert "Width" in proj.variables       # found in the nested designMaster
    assert "GoToForm" in proj.spec_macros  # found in the nested project.xml
