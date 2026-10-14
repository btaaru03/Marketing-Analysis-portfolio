"""
tasks/quantitative_task.py
===========================
Builds Task 1 — the Quantitative Analyst's Initial Mandate.

Responsibility
--------------
Takes the pre-formatted row_context string for a single sub-category and
instructs the Quantitative Data Analyst to issue a rigid, numbers-first
capital allocation directive based exclusively on BCG positioning and YoY
financial trajectory.

Input dependency  : row_context string (produced by utils/context_builder.py)
Output consumed by: Task 2 (strategic_task) via context=[task_quantitative]
"""

from __future__ import annotations

from crewai import Agent, Task


def build_quantitative_task(
    row_context: str,
    quantitative_analyst: Agent,
) -> Task:
    """
    Construct the Quantitative Review task for a single sub-category.

    Parameters
    ----------
    row_context : str
        Pre-formatted metric block for the sub-category under review.
    quantitative_analyst : Agent
        The Quantitative Data Analyst agent that will execute this task.

    Returns
    -------
    Task
        A fully configured CrewAI Task assigned to the quantitative_analyst.
    """
    return Task(
        description=(
            f"You are reviewing the following product sub-category metrics:\n\n"
            f"{row_context}\n\n"
            "Based exclusively on the BCG matrix quadrant, market growth rate, "
            "relative market share, and the year-over-year profit trajectory, "
            "issue a rigid initial mandate. State clearly:\n\n"
            "1. The BCG classification and what it unambiguously demands.\n"
            "2. The YoY profit change in both absolute dollars and percentage — "
            "state whether the trajectory is improving or declining.\n"
            "3. Your initial capital allocation recommendation "
            "(Invest / Protect / Restructure / Liquidate) with hard numerical "
            "justification for every claim.\n\n"
            "Be blunt, concise, and numbers-first. No soft language. No hedging."
        ),
        expected_output=(
            "A structured Initial Mandate Report (300 words maximum) containing:\n"
            "- **BCG Label & Mandate**: classification and what it demands\n"
            "- **YoY Profit Trend**: absolute change, percentage change, direction\n"
            "- **Initial Recommendation**: Invest / Protect / Restructure / Liquidate "
            "with numerical justification"
        ),
        agent=quantitative_analyst,
    )
