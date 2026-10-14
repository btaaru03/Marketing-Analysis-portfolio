"""
tasks/strategic_task.py
========================
Builds Task 2 — the Strategic Challenger's Audit.

Responsibility
--------------
Receives Task 1's output via context chaining and scrutinises the
Quantitative Analyst's mandate against profit_margin_pct.

Rules baked into the task description
--------------------------------------
- Margin > HIGH_MARGIN_THRESHOLD  →  aggressively challenge any Liquidate
  or Restructure directive; cite margin efficiency, YoY profit growth, and
  the risk of destroying a high-yield asset.
- Margin ≤ HIGH_MARGIN_THRESHOLD  →  acknowledge the mandate may be sound
  but still probe for mitigating factors (sales growth, emerging position).
- Close with a declared Strategic Position:
  Support | Partial Support | Object

Input dependency  : task_quantitative (passed as context)
Output consumed by: Task 3 (verdict_task) via context=[task_quantitative, task_strategic]
"""

from __future__ import annotations

from crewai import Agent, Task

from config.settings import HIGH_MARGIN_THRESHOLD


def build_strategic_task(
    row_context: str,
    strategic_challenger: Agent,
    task_quantitative: Task,
) -> Task:
    """
    Construct the Strategic Audit task for a single sub-category.

    Parameters
    ----------
    row_context : str
        Pre-formatted metric block for the sub-category under review.
    strategic_challenger : Agent
        The Strategic Growth Challenger agent that will execute this task.
    task_quantitative : Task
        The completed Quantitative Review task — passed as context so the
        challenger can read the analyst's mandate before responding.

    Returns
    -------
    Task
        A fully configured CrewAI Task assigned to the strategic_challenger.
    """
    return Task(
        description=(
            "The Quantitative Analyst has issued an initial mandate. "
            "Review their output carefully before forming your response.\n\n"
            f"Sub-category metrics under review:\n{row_context}\n\n"
            "Your job:\n\n"
            f"1. If profit_margin_pct is **above {HIGH_MARGIN_THRESHOLD}%**, "
            "aggressively challenge any Liquidate or Restructure recommendation. "
            "Build a detailed case citing margin efficiency, absolute YoY profit "
            "growth, and the corporate risk of liquidating a high-yield asset.\n\n"
            f"2. If profit_margin_pct is **at or below {HIGH_MARGIN_THRESHOLD}%**, "
            "acknowledge the analyst's mandate may be sound — but still probe for "
            "mitigating factors such as rapid sales growth, an emerging niche "
            "market position, or strong absolute profit levels.\n\n"
            "3. Close with your declared **Strategic Position**:\n"
            "   - Support\n"
            "   - Partial Support\n"
            "   - Object"
        ),
        expected_output=(
            "A Strategic Audit Report (300 words maximum) containing:\n"
            "- **Margin Assessment**: is the margin high or low, and what does it mean?\n"
            "- **Objections or Supporting Arguments**: specific data-backed points\n"
            "- **Strategic Position**: Support | Partial Support | Object"
        ),
        agent=strategic_challenger,
        context=[task_quantitative],
    )
