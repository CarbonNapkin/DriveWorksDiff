"""
Data models for DriveWorks project elements.
"""

from dataclasses import dataclass, field


@dataclass
class Variable:
    name: str
    store_name: str = ""
    formula: str = ""
    comment: str = ""
    category: str = ""


@dataclass
class Constant:
    name: str
    store_name: str = ""
    value: str = ""
    comment: str = ""


@dataclass
class CalcTable:
    name: str
    row_count: int = 0
    columns: dict = field(default_factory=dict)  # col_name -> {common: str, rows: {idx: str}}


@dataclass
class ComponentTask:
    id: str
    name: str
    task_type: str
    component_id: str = ""
    scope: str = ""
    rules: dict = field(default_factory=dict)  # rule_name -> formula


@dataclass
class SpecMacroTask:
    title: str = ""
    task_type: str = ""
    # Property name -> formula string. Empty formula means a static value.
    properties: dict = field(default_factory=dict)


@dataclass
class SpecMacro:
    name: str
    # Ordered by appearance in the XML so reordering shows up in diffs.
    tasks: list = field(default_factory=list)


@dataclass
class NavStep:
    name: str
    step_type: str = ""
    next_step_rule: str = ""
    next_step_value: str = ""
    next_macro_value: str = ""
    previous_macro_value: str = ""


@dataclass
class DataTableDef:
    name: str
    table_type: str = ""


@dataclass
class FormControl:
    name: str
    control_type: str = ""
    # property name -> (is_static, formula_or_value)
    props: dict = field(default_factory=dict)


@dataclass
class Form:
    name: str
    # form-level rule-bearing properties (same shape as control props)
    form_props: dict = field(default_factory=dict)
    # control name -> FormControl
    controls: dict = field(default_factory=dict)


@dataclass
class DWProject:
    """Holds all parsed DriveWorks project data"""
    name: str = ""
    variables: dict = field(default_factory=dict)
    constants: dict = field(default_factory=dict)
    calc_tables: dict = field(default_factory=dict)
    component_tasks: dict = field(default_factory=dict)
    documents: dict = field(default_factory=dict)
    lookup_tables: dict = field(default_factory=dict)
    spec_macros: dict = field(default_factory=dict)
    nav_steps: dict = field(default_factory=dict)
    data_tables: dict = field(default_factory=dict)
    forms: dict = field(default_factory=dict)
    # GUID -> human-readable name, used to resolve Variable.category
    categories: dict = field(default_factory=dict)
