"""Tests for the XML parsers: a small project parses into the expected models,
and malformed input degrades gracefully instead of crashing."""

from dw_compare.parsers import (
    parse_project_xml, parse_design_master, parse_component_tasks, load_project,
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
    assert data["special_vars"]["R"]["rule"] == '="A"'
    assert "L" in data["lookup_tables"]
    assert "Start" in data["nav_steps"]


def test_parse_component_tasks(tmp_path):
    p = tmp_path / "componentTasks.xml"
    p.write_text(CT_XML, encoding="utf-8")
    tasks = parse_component_tasks(p)
    assert len(tasks) == 1
    task = next(iter(tasks.values()))
    assert task.name == "Gen"
    assert task.rules["Tmpl"] == '="A3"'


def test_load_project_end_to_end(tmp_path):
    (tmp_path / "project.xml").write_text(PROJECT_XML, encoding="utf-8")
    (tmp_path / "designMaster.xml").write_text(DESIGN_XML, encoding="utf-8")
    (tmp_path / "componentTasks.xml").write_text(CT_XML, encoding="utf-8")
    proj = load_project(tmp_path)
    assert "W" in proj.variables
    assert "M" in proj.constants
    assert proj.component_tasks
