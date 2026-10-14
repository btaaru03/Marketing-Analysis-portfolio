"""
main.py
========
Entry point for the Executive Strategy Brief Generator.

This file is intentionally thin — all logic lives in the packages below.
Its only job is to wire the four pipeline stages together and handle the
top-level I/O (print banner, save report, print report).

Pipeline
--------
  1. config/settings.py   → build_llm()          — initialise Gemini LLM
  2. utils/data_loader.py → load_portfolio_data() — load & validate CSV
  3. crew/strategy_crew.py→ run_analysis()        — run 3-agent debate per row
  4. utils/report_compiler→ compile_report()      — assemble Markdown brief
  5. main.py              → write file + print    — deliver output

Run
---
    pip install -r requirements.txt
    python main.py
"""

from __future__ import annotations

import sys

from config.settings import OUTPUT_PATH, GEMINI_MODEL, build_llm
from utils.data_loader import load_portfolio_data
from utils.models import SubCategoryResult
from utils.report_compiler import compile_report
from crew.strategy_crew import run_analysis


def _save_brief(results: list[SubCategoryResult], *, partial: bool) -> str:
    """Compile the Markdown brief and write it immediately so it is visible mid-run."""
    report = compile_report(results)
    try:
        OUTPUT_PATH.write_text(report, encoding="utf-8")
        label = "Partial" if partial else "Final"
        print(
            f"  ↳ {label} brief saved ({len(results)} categor"
            f"{'y' if len(results) == 1 else 'ies'}) → {OUTPUT_PATH.resolve()}",
            flush=True,
        )
    except OSError as exc:
        print(f"[WARNING] Could not write report file: {exc}", file=sys.stderr)
    return report


def _on_result(
    _latest: SubCategoryResult,
    results_so_far: list[SubCategoryResult],
    total: int,
) -> None:
    _save_brief(results_so_far, partial=len(results_so_far) < total)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _print_banner(title: str) -> None:
    """Print a consistent section banner to stdout."""
    bar = "=" * 70
    print(f"\n{bar}\n  {title}\n{bar}\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _print_banner("EXECUTIVE STRATEGY BRIEF GENERATOR  |  CrewAI + Google Gemini")

    # ── Stage 1: Initialise LLM ───────────────────────────────────────────────
    print("Initialising Gemini LLM...")
    llm = build_llm()
    print(f"✓  LLM ready  ({GEMINI_MODEL})\n")

    # ── Stage 2: Load & validate data ─────────────────────────────────────────
    df = load_portfolio_data()   # exits with a clear message on any error

    # ── Stage 3: Run adversarial debate for every sub-category ────────────────
    _print_banner(f"STARTING ANALYSIS  |  {len(df)} sub-categories")
    print(
        f"Open this file while it runs — it updates after every sub-category:\n"
        f"  {OUTPUT_PATH.resolve()}\n",
        flush=True,
    )

    results: list[SubCategoryResult] = run_analysis(
        df=df, llm=llm, on_result=_on_result
    )

    # ── Stage 4–5: Final compile + save ───────────────────────────────────────
    _print_banner("COMPILING EXECUTIVE STRATEGY BRIEF")
    report: str = _save_brief(results, partial=False)

    # ── Stage 6: Print report to terminal ─────────────────────────────────────
    _print_banner("EXECUTIVE STRATEGY BRIEF  —  TERMINAL OUTPUT")
    print(report)


if __name__ == "__main__":
    main()
