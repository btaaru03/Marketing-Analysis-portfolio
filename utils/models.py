"""
utils/models.py
================
Shared data container used across the entire pipeline.

SubCategoryResult is the single unit of data that flows from
crew/strategy_crew.py through to utils/report_compiler.py.
Keeping it in utils/models.py prevents circular imports — any
module can import it without pulling in crew or agent logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SubCategoryResult:
    """
    Holds all three agent outputs produced for one sub-category row.

    Attributes
    ----------
    sub_category : str
        Name of the product sub-category (e.g. 'Copiers').
    math_quadrant : str
        BCG matrix label: 'Star' | 'Cash Cow' | 'Question Mark' | 'Dog'.
    profit_margin_pct : float
        Profit margin percentage from the source CSV.
    quantitative_output : str
        Raw text output from the Quantitative Data Analyst (Task 1).
    strategic_output : str
        Raw text output from the Strategic Growth Challenger (Task 2).
    final_verdict : str
        Raw text output from the Chief of Staff (Task 3).
        Contains the structured Markdown verdict block used by the compiler.
    error : Optional[str]
        Populated only when processing fails; None on success.
    """

    sub_category: str
    math_quadrant: str
    profit_margin_pct: float
    quantitative_output: str = ""
    strategic_output: str = ""
    final_verdict: str = ""
    error: Optional[str] = None
