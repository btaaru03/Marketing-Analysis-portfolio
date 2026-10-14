"""
agents package
==============
Exports all three CrewAI agent factory functions so callers can do:

    from agents import build_quantitative_analyst, build_strategic_challenger, build_chief_of_staff
"""

from agents.quantitative_analyst import build_quantitative_analyst
from agents.strategic_challenger import build_strategic_challenger
from agents.chief_of_staff import build_chief_of_staff

__all__ = [
    "build_quantitative_analyst",
    "build_strategic_challenger",
    "build_chief_of_staff",
]
