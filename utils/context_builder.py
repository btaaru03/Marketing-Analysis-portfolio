"""
utils/context_builder.py
=========================
Converts a single pandas DataFrame row into a clean, human-readable
metric block that the CrewAI agents reason over.

The formatted string is intentionally verbose and structured so that
the LLM does not have to infer units, directions, or comparisons —
every derived metric (YoY changes, percentages) is pre-computed here
and handed to the agents as plain text.

Public API
----------
    build_row_context(row: pd.Series) -> str
"""

from __future__ import annotations

import textwrap

import pandas as pd


def build_row_context(row: pd.Series) -> str:
    """
    Build a pre-formatted metric context string for one sub-category row.

    Computes the following derived metrics before formatting:
    - YoY absolute profit change  ($)
    - YoY profit change           (%)
    - YoY sales change            (%)

    Division-by-zero is handled gracefully — any zero base returns 0.0%.

    Parameters
    ----------
    row : pd.Series
        A single row from the portfolio DataFrame produced by data_loader.

    Returns
    -------
    str
        A multi-line, UTF-8 string ready to be embedded in a task
        description prompt.
    """

    profit_change: float = float(row["Profit_2014"]) - float(row["Profit_2013"])

    profit_change_pct: float = (
        (profit_change / abs(float(row["Profit_2013"]))) * 100
        if float(row["Profit_2013"]) != 0
        else 0.0
    )

    sales_change_pct: float = (
        ((float(row["Sales_2014"]) - float(row["Sales_2013"]))
         / abs(float(row["Sales_2013"]))) * 100
        if float(row["Sales_2013"]) != 0
        else 0.0
    )

    return textwrap.dedent(f"""
        Sub-Category       : {row['Sub-Category']}
        BCG Quadrant       : {row['math_quadrant']}
        ─────────────────────────────────────────────
        Sales 2013         : ${float(row['Sales_2013']):>14,.2f}
        Sales 2014         : ${float(row['Sales_2014']):>14,.2f}
        Sales Growth YoY   : {sales_change_pct:>+.2f}%
        ─────────────────────────────────────────────
        Profit 2013        : ${float(row['Profit_2013']):>14,.2f}
        Profit 2014        : ${float(row['Profit_2014']):>14,.2f}
        Profit Change YoY  : ${profit_change:>+,.2f}  ({profit_change_pct:>+.2f}%)
        ─────────────────────────────────────────────
        Profit Margin %    : {float(row['profit_margin_pct']):.2f}%
        Market Growth Rate : {float(row['market_growth_rate']):.4f}  \
({float(row['market_growth_rate']) * 100:.2f}%)
        Rel. Market Share  : {float(row['relative_market_share']):.4f}
        ─────────────────────────────────────────────
    """).strip()
