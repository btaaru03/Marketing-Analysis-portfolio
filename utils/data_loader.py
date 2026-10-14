"""
utils/data_loader.py
=====================
Handles all CSV I/O for the pipeline.

Responsibilities
----------------
- Locate and open mined_portfolio_data.csv via the path in config/settings.py.
- Validate that every required column is present before handing the
  DataFrame to the caller.
- Exit clearly with a diagnostic message on any file or schema error —
  never let a KeyError surface deep inside the agent loop.

Public API
----------
    load_portfolio_data() -> pd.DataFrame
"""

from __future__ import annotations

import sys

import pandas as pd

from config.settings import CSV_PATH
REQUIRED_COLUMNS: frozenset[str] = frozenset({
    "Sub-Category",
    "Profit_2013",
    "Profit_2014",
    "Sales_2013",
    "Sales_2014",
    "market_growth_rate",
    "relative_market_share",
    "profit_margin_pct",
    "math_quadrant",
})


def load_portfolio_data() -> pd.DataFrame:
    """
    Load and validate the portfolio CSV.

    Returns
    -------
    pd.DataFrame
        A clean DataFrame with all required columns present and dtypes
        inferred by pandas.

    Raises / Exits
    --------------
    SystemExit
        - If the file does not exist at CSV_PATH.
        - If the file cannot be parsed as CSV.
        - If one or more required columns are missing.
    """
    if not CSV_PATH.exists():
        sys.exit(
            f"[FATAL] Data file not found: {CSV_PATH.resolve()}\n"
            "Ensure 'mined_portfolio_data.csv' sits in the project root "
            "alongside main.py."
        )

    try:
        df: pd.DataFrame = pd.read_csv(CSV_PATH)
    except Exception as exc:
        sys.exit(f"[FATAL] Failed to read CSV at {CSV_PATH}: {exc}")

    missing: frozenset[str] = REQUIRED_COLUMNS - frozenset(df.columns)
    if missing:
        sys.exit(
            f"[FATAL] CSV is missing required columns: {sorted(missing)}\n"
            f"Found columns: {list(df.columns)}"
        )

    print(f"✓  Loaded {len(df)} sub-categories from '{CSV_PATH.name}'")
    return df
