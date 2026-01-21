"""
DriveWorks Project Comparison Tool

A tool to compare two versions of a DriveWorks project and generate an HTML report
showing all differences in variables, constants, calculation tables, and more.
"""

from .models import Variable, Constant, CalcTable, ComponentTask, DWProject
from .parsers import load_project
from .report import generate_html_report

__version__ = '1.0.0'
__all__ = [
    'Variable',
    'Constant', 
    'CalcTable',
    'ComponentTask',
    'DWProject',
    'load_project',
    'generate_html_report',
]
