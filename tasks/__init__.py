"""
tasks package
=============
Exports all three CrewAI task factory functions so callers can do:

    from tasks import build_quantitative_task, build_strategic_task, build_verdict_task

Each factory takes a row_context string plus the relevant agent(s) and
upstream task(s), and returns a fully wired CrewAI Task.
"""

from tasks.quantitative_task import build_quantitative_task
from tasks.strategic_task import build_strategic_task
from tasks.verdict_task import build_verdict_task

__all__ = [
    "build_quantitative_task",
    "build_strategic_task",
    "build_verdict_task",
]
