"""
tasks/verdict_task.py
======================
Builds Task 3 — the Chief of Staff's Final Verdict.

Responsibility
--------------
Receives both previous task outputs via context chaining, mediates the
debate, and renders a single binding corporate verdict in structured
Markdown that the report compiler can parse directly.

Verdict labels (exactly one must appear in output)
---------------------------------------------------
  Invest | Protect | Restructure | Liquidate

Output format (enforced in expected_output)
-------------------------------------------
  **Sub-Category:** <name>
  **BCG Quadrant:** <quadrant>
  **Final Verdict:** <label>
  **Verdict Rationale:** <2-4 sentences>
  **Priority Actions:**
  - <action 1>
  - <action 2>
  - <action 3>

Input dependency  : task_quantitative + task_strategic (both passed as context)
Output consumed by: utils/report_compiler.py via SubCategoryResult.final_verdict
"""

from __future__ import annotations

from crewai import Agent, Task


def build_verdict_task(
    row_context: str,
    chief_of_staff: Agent,
    task_quantitative: Task,
    task_strategic: Task,
) -> Task:
    """
    Construct the Executive Final Verdict task for a single sub-category.

    Parameters
    ----------
    row_context : str
        Pre-formatted metric block for the sub-category under review.
    chief_of_staff : Agent
        The Chief of Staff / Corporate Arbitrator agent that will execute
        this task.
    task_quantitative : Task
        The completed Quantitative Review task — passed as context.
    task_strategic : Task
        The completed Strategic Audit task — passed as context.

    Returns
    -------
    Task
        A fully configured CrewAI Task assigned to the chief_of_staff.
    """
    return Task(
        description=(
            "You have reviewed the Quantitative Analyst's Initial Mandate and the "
            "Strategic Challenger's Audit. Now render the final binding corporate "
            "verdict that the executive team will act on.\n\n"
            f"Sub-category metrics for reference:\n{row_context}\n\n"
            "Your output MUST follow this exact Markdown structure:\n\n"
            "---\n"
            "**Sub-Category:** <name>\n"
            "**BCG Quadrant:** <quadrant>\n"
            "**Final Verdict:** <Invest | Protect | Restructure | Liquidate>\n"
            "**Verdict Rationale:** <2–4 sentences that ground the decision in "
            "the numerical data and the debate above>\n"
            "**Priority Actions:**\n"
            "- <Immediate action 1 for the executive team>\n"
            "- <Immediate action 2 for the executive team>\n"
            "- <Immediate action 3 for the executive team>\n"
            "---\n\n"
            "Be decisive. One verdict label only. No ambiguity."
        ),
        expected_output=(
            "A Final Verdict Block in structured Markdown (250 words maximum) "
            "containing exactly:\n"
            "- **Sub-Category** field\n"
            "- **BCG Quadrant** field\n"
            "- **Final Verdict** field: one of Invest | Protect | Restructure | Liquidate\n"
            "- **Verdict Rationale** field: 2–4 sentences\n"
            "- **Priority Actions** field: exactly 3 bullet points"
        ),
        agent=chief_of_staff,
        context=[task_quantitative, task_strategic],
    )
