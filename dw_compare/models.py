"""
Data models for DriveWorks project elements.
"""

from dataclasses import dataclass, field
from typing import Optional


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
class CalcTableCell:
    formula: str = ""
    row_index: Optional[int] = None  # None = common rule


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
class DWProject:
    """Holds all parsed DriveWorks project data"""
    name: str = ""
    variables: dict = field(default_factory=dict)
    constants: dict = field(default_factory=dict)
    special_vars: dict = field(default_factory=dict)
    calc_tables: dict = field(default_factory=dict)
    component_tasks: dict = field(default_factory=dict)
    documents: dict = field(default_factory=dict)
    lookup_tables: dict = field(default_factory=dict)
