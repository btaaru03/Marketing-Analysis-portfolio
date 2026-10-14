"""
crew/strategy_crew.py
======================
Runs one sequential three-agent debate per sub-category.

Free-tier Gemini cannot absorb parallel crews (6 rows × 3 calls). Parallel
batches look "stuck" after the first Done line because the other workers
are retrying 429s with stdout silenced, and the Markdown brief is only
compiled after all 17 rows finish.

This module therefore:
  * processes one sub-category at a time
  * pauses between rows
  * retries 429/503 with the API-suggested delay
  * notifies the caller after every row so the brief can be written live
"""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Callable
from typing import Optional

import pandas as pd
from crewai import Crew, Process

from agents import (
    build_chief_of_staff,
    build_quantitative_analyst,
    build_strategic_challenger,
)
from config.settings import INTER_ROW_PAUSE_SECONDS, MAX_RETRIES, RETRY_BASE_DELAY
from tasks import (
    build_quantitative_task,
    build_strategic_task,
    build_verdict_task,
)
from utils.context_builder import build_row_context
from utils.models import SubCategoryResult

logging.getLogger("crewai").setLevel(logging.ERROR)
logging.getLogger("litellm").setLevel(logging.ERROR)
logging.getLogger("opentelemetry").setLevel(logging.ERROR)

OnResult = Callable[[SubCategoryResult, list[SubCategoryResult], int], None]


def _extract_retry_delay(exc: Exception) -> float | None:
    match = re.search(r"retry[^\d]*(\d+(?:\.\d+)?)\s*s", str(exc), re.IGNORECASE)
    return float(match.group(1)) if match else None


def _is_retryable(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(
        k in text
        for k in (
            "ratelimiterror",
            "429",
            "resource_exhausted",
            "quota",
            "503",
            "serviceunavailableerror",
            "unavailable",
            "high demand",
        )
    )


def _verdict_label(text: str) -> str:
    match = re.search(
        r"Final Verdict:?\*{0,2}\s*:?\s*\*{0,2}\s*(Invest|Protect|Restructure|Liquidate)\b",
        text or "",
        re.IGNORECASE,
    )
    return match.group(1).title() if match else "Pending"


def _kickoff_with_retry(crew: Crew, sub_cat: str, inputs: dict) -> object:
    delay = RETRY_BASE_DELAY
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return crew.kickoff(inputs=inputs)
        except Exception as exc:
            if not _is_retryable(exc):
                raise
            is_overload = "503" in str(exc) or "unavailable" in str(exc).lower()
            wait = 30.0 if is_overload else ((_extract_retry_delay(exc) or delay) + 5.0)
            if attempt < MAX_RETRIES:
                print(
                    f"  [RETRY] '{sub_cat}' attempt {attempt}/{MAX_RETRIES} "
                    f"— waiting {wait:.0f}s...",
                    flush=True,
                )
                time.sleep(wait)
                delay = min(delay * 2, 300.0)
            else:
                raise RuntimeError(
                    f"All {MAX_RETRIES} retries exhausted for '{sub_cat}'."
                ) from exc


def _analyse_row(
    row: pd.Series,
    llm: str,
    loop_idx: int,
    total: int,
) -> SubCategoryResult:
    sub_cat: str = str(row["Sub-Category"])
    quadrant: str = str(row["math_quadrant"])
    margin: float = float(row["profit_margin_pct"])

    print(
        f"\n  → [{loop_idx}/{total}] {sub_cat} ({quadrant}, margin {margin:.2f}%)"
        "  — 3 agent calls, usually 30–90s",
        flush=True,
    )

    result = SubCategoryResult(
        sub_category=sub_cat,
        math_quadrant=quadrant,
        profit_margin_pct=margin,
    )

    try:
        analyst = build_quantitative_analyst(llm)
        challenger = build_strategic_challenger(llm)
        cos = build_chief_of_staff(llm)

        row_context = build_row_context(row)
        task_q = build_quantitative_task(
            row_context=row_context, quantitative_analyst=analyst
        )
        task_s = build_strategic_task(
            row_context=row_context,
            strategic_challenger=challenger,
            task_quantitative=task_q,
        )
        task_v = build_verdict_task(
            row_context=row_context,
            chief_of_staff=cos,
            task_quantitative=task_q,
            task_strategic=task_s,
        )

        crew = Crew(
            agents=[analyst, challenger, cos],
            tasks=[task_q, task_s, task_v],
            process=Process.sequential,
            verbose=False,
            memory=False,
        )

        crew_output = _kickoff_with_retry(
            crew=crew, sub_cat=sub_cat, inputs={"sub_category": sub_cat}
        )
        task_outputs = (
            crew_output.tasks_output if hasattr(crew_output, "tasks_output") else []
        )

        result.quantitative_output = (
            task_outputs[0].raw if len(task_outputs) > 0 else str(crew_output)
        )
        result.strategic_output = task_outputs[1].raw if len(task_outputs) > 1 else ""
        result.final_verdict = (
            task_outputs[2].raw if len(task_outputs) > 2 else str(crew_output)
        )

        print(
            f"  ✓ [{loop_idx}/{total}] {sub_cat}  →  {_verdict_label(result.final_verdict)}",
            flush=True,
        )

    except Exception as exc:
        print(f"  ✗ [{loop_idx}/{total}] {sub_cat} — {exc}", flush=True)
        result.error = str(exc)
        result.final_verdict = (
            f"**Sub-Category:** {sub_cat}\n"
            f"**BCG Quadrant:** {quadrant}\n"
            f"**Final Verdict:** ANALYSIS ERROR\n"
            f"**Verdict Rationale:** Processing failed — {exc}\n"
            f"**Priority Actions:**\n"
            f"- Retry analysis with corrected input data\n"
            f"- Validate GEMINI_API_KEY and check rate limits\n"
            f"- Review sub-category data for anomalies\n"
        )

    return result


def run_analysis(
    df: pd.DataFrame,
    llm: str,
    on_result: Optional[OnResult] = None,
) -> list[SubCategoryResult]:
    """
    Process every sub-category sequentially.

    on_result, if provided, is called after each row with
    (latest_result, results_so_far, total_rows) so the brief can be saved live.
    """
    total = len(df)
    results: list[SubCategoryResult] = []

    print(
        f"\n  {total} sub-categories, one at a time "
        f"(pause {INTER_ROW_PAUSE_SECONDS:.0f}s between rows).\n"
        "  The brief is rewritten after each finished category.\n",
        flush=True,
    )

    for loop_idx, (_, row) in enumerate(df.iterrows(), start=1):
        result = _analyse_row(row=row, llm=llm, loop_idx=loop_idx, total=total)
        results.append(result)
        if on_result is not None:
            on_result(result, results, total)
        if loop_idx < total:
            print(
                f"  [PAUSE] {INTER_ROW_PAUSE_SECONDS:.0f}s before the next sub-category...",
                flush=True,
            )
            time.sleep(INTER_ROW_PAUSE_SECONDS)

    return results