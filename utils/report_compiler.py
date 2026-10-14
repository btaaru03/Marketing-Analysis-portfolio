"""
utils/report_compiler.py
=========================
Assembles the final Markdown Executive Strategy Brief from the list of
SubCategoryResult objects produced by crew/strategy_crew.py.

Structure of the generated report
----------------------------------
  # Executive Strategy Brief
  ## 1. Portfolio Health Summary        — BCG distribution + verdict distribution
  ## 2. Categorised Allocation Mandates — Invest / Protect / Restructure / Liquidate
  ## 3. Agentic Argument Logs           — full debate transcript per sub-category
  ## ⚠️ Processing Errors              — only present if any rows errored

Bucketing logic
---------------
The final_verdict text from the Chief of Staff is scanned for the first
occurrence of a verdict keyword (case-insensitive):
  INVEST → invest bucket
  PROTECT → protect bucket
  RESTRUCTURE → restructure bucket
  LIQUIDATE → liquidate bucket
  (none found) → restructure bucket (safe default — flags for human review)

Public API
----------
    compile_report(results: list[SubCategoryResult]) -> str
"""

from __future__ import annotations

import re
from datetime import datetime

from config.settings import GEMINI_MODEL
from utils.models import SubCategoryResult

def _verdict_table(items: list[SubCategoryResult]) -> str:
    """Render a compact Markdown summary table for a verdict bucket."""
    if not items:
        return "_No sub-categories in this bucket._\n"
    header = (
        "| Sub-Category | BCG Quadrant | Profit Margin |\n"
        "|---|---|---|\n"
    )
    rows = "\n".join(
        f"| {r.sub_category} | {r.math_quadrant} | {r.profit_margin_pct:.2f}% |"
        for r in items
    )
    return header + rows + "\n"


def _verdict_blocks(items: list[SubCategoryResult]) -> str:
    """Render the full Chief of Staff verdict block for each item in a bucket."""
    if not items:
        return "_No sub-categories in this bucket._\n\n"
    return "\n\n".join(r.final_verdict for r in items) + "\n\n"


def _argument_log(r: SubCategoryResult) -> str:
    """Render the complete three-agent debate transcript for one sub-category."""
    lines = [
        f"### {r.sub_category}  ·  {r.math_quadrant}  ·  Margin: {r.profit_margin_pct:.2f}%",
        "",
        "#### 🔢 Quantitative Analyst — Initial Mandate",
        r.quantitative_output or "_No output captured._",
        "",
        "#### ⚔️  Strategic Challenger — Audit",
        r.strategic_output or "_No output captured._",
        "",
        "#### ⚖️  Chief of Staff — Final Verdict",
        r.final_verdict or "_No output captured._",
        "",
        "---",
    ]
    return "\n".join(lines)


_VERDICT_RE = re.compile(
    r"\*{0,2}Final Verdict:?\*{0,2}\s*:?\s*\*{0,2}\s*(Invest|Protect|Restructure|Liquidate)\b",
    re.IGNORECASE,
)


def _parse_verdict(text: str) -> str | None:
    """Read ONLY the '**Final Verdict:** <label>' line, not the whole text."""
    match = _VERDICT_RE.search(text or "")
    return match.group(1).upper() if match else None


def _bucket_results(
    results: list[SubCategoryResult],
) -> tuple[
    list[SubCategoryResult],
    list[SubCategoryResult],
    list[SubCategoryResult],
    list[SubCategoryResult],
    list[SubCategoryResult],
]:
    """
    Partition results into (invest, protect, restructure, liquidate, errors).

    Scans r.final_verdict upper-cased for the first matching keyword.
    Rows with r.error set are placed in the errors bucket regardless of verdict.
    """
    invest: list[SubCategoryResult] = []
    protect: list[SubCategoryResult] = []
    restructure: list[SubCategoryResult] = []
    liquidate: list[SubCategoryResult] = []
    errors: list[SubCategoryResult] = []

    for r in results:
        if r.error:
            errors.append(r)
            continue
        label = _parse_verdict(r.final_verdict)
        if label == "INVEST":
            invest.append(r)
        elif label == "PROTECT":
            protect.append(r)
        elif label == "RESTRUCTURE":
            restructure.append(r)
        elif label == "LIQUIDATE":
            liquidate.append(r)
        else:
            restructure.append(r)

    return invest, protect, restructure, liquidate, errors


def compile_report(results: list[SubCategoryResult]) -> str:
    """
    Assemble a complete Markdown Executive Strategy Brief.

    Parameters
    ----------
    results : list[SubCategoryResult]
        All per-row results collected from crew/strategy_crew.py.

    Returns
    -------
    str
        A UTF-8 Markdown string ready to be written to disk and printed.
    """
    now: str = datetime.now().strftime("%B %d, %Y — %H:%M")
    invest, protect, restructure, liquidate, errors = _bucket_results(results)

    stars     = [r.sub_category for r in results if r.math_quadrant == "Star"]
    cows      = [r.sub_category for r in results if r.math_quadrant == "Cash Cow"]
    questions = [r.sub_category for r in results if r.math_quadrant == "Question Mark"]
    dogs      = [r.sub_category for r in results if r.math_quadrant == "Dog"]

    sections: list[str] = []

    sections.append(
        "# Executive Strategy Brief\n"
        "## AI-Orchestrated Portfolio Review — Global Superstore\n\n"
        f"> **Generated:** {now}  \n"
        f"> **Model:** {GEMINI_MODEL}  \n"
        "> **Framework:** CrewAI Adversarial Debate (3-Agent Sequential)  \n"
        f"> **Sub-Categories Analysed:** {len(results)}  \n\n"
        "---\n"
    )

    sections.append(
        "## 1. Portfolio Health Summary\n\n"
        "### BCG Matrix Distribution\n\n"
        "| BCG Class | Count | Sub-Categories |\n"
        "|---|---|---|\n"
        f"| 🌟 Star         | {len(stars)}     | {', '.join(stars) if stars else '—'} |\n"
        f"| 🐄 Cash Cow     | {len(cows)}      | {', '.join(cows) if cows else '—'} |\n"
        f"| ❓ Question Mark | {len(questions)} | {', '.join(questions) if questions else '—'} |\n"
        f"| 🐕 Dog          | {len(dogs)}      | {', '.join(dogs) if dogs else '—'} |\n\n"
        "### Agentic Verdict Distribution\n\n"
        "| Mandate     | Count |\n"
        "|---|---|\n"
        f"| 🟢 Invest      | {len(invest)} |\n"
        f"| 🔵 Protect     | {len(protect)} |\n"
        f"| 🟡 Restructure | {len(restructure)} |\n"
        f"| 🔴 Liquidate   | {len(liquidate)} |\n"
        f"| ⚠️  Error       | {len(errors)} |\n\n"
        "---\n"
    )

    sections.append(
        "## 2. Categorised Allocation Mandates\n\n"
        "### 🟢 INVEST\n\n"
        f"{_verdict_table(invest)}\n"
        f"{_verdict_blocks(invest)}"
        "### 🔵 PROTECT\n\n"
        f"{_verdict_table(protect)}\n"
        f"{_verdict_blocks(protect)}"
        "### 🟡 RESTRUCTURE\n\n"
        f"{_verdict_table(restructure)}\n"
        f"{_verdict_blocks(restructure)}"
        "### 🔴 LIQUIDATE\n\n"
        f"{_verdict_table(liquidate)}\n"
        f"{_verdict_blocks(liquidate)}"
        "---\n"
    )

    sections.append("## 3. Agentic Argument Logs _(Appendix)_\n\n")
    for r in results:
        sections.append(_argument_log(r) + "\n\n")

    if errors:
        sections.append("## ⚠️ Processing Errors\n\n")
        for r in errors:
            sections.append(f"- **{r.sub_category}**: {r.error}\n")

    return "\n".join(sections)