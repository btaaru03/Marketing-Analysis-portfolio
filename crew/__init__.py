"""
crew package
============
Exports the main analysis runner so callers can do:

    from crew import run_analysis
"""

from crew.strategy_crew import run_analysis

__all__ = ["run_analysis"]
