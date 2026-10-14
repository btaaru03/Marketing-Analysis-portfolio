"""
utils package
=============
Shared utilities used across the pipeline.

Modules
-------
models.py          — SubCategoryResult dataclass (shared data container)
data_loader.py     — CSV loading and schema validation
context_builder.py — Converts a DataFrame row into an agent-readable string
report_compiler.py — Assembles the final Markdown Executive Strategy Brief
"""

from utils.models import SubCategoryResult
from utils.data_loader import load_portfolio_data
from utils.context_builder import build_row_context
from utils.report_compiler import compile_report

__all__ = [
    "SubCategoryResult",
    "load_portfolio_data",
    "build_row_context",
    "compile_report",
]
