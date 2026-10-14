"""
config/settings.py
==================
Central configuration: all project-wide constants and the LLM factory.
Every other module imports from here — no magic strings anywhere else.

LLM strategy
------------
CrewAI routes all LLM calls through LiteLLM internally.  Passing a
LangChain ChatGoogleGenerativeAI object causes LiteLLM to serialise it
as a string and lose the provider prefix, producing the error:
    "LLM Provider NOT provided ... model='models/gemini-1.5-flash'"

The correct approach is to:
  1. Use LiteLLM's provider-prefixed model string: "gemini/gemini-1.5-flash"
  2. Expose the key as GOOGLE_API_KEY in the environment — LiteLLM reads
     this automatically for the gemini/ provider.
  3. Return the plain model-name string from build_llm(); CrewAI agents
     accept a string for their `llm` parameter.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")


CSV_PATH: Path = _PROJECT_ROOT / "mined_portfolio_data.csv"
OUTPUT_PATH: Path = _PROJECT_ROOT / "Executive_Strategy_Brief.md"

GEMINI_MODEL: str = "gemini/gemini-flash-lite-latest"


HIGH_MARGIN_THRESHOLD: float = 15.0

GROWTH_THRESHOLD: float = 0.20   
SHARE_THRESHOLD: float = 0.50  

AGENT_MAX_ITER: int = 2
AGENT_MAX_RPM: int = 8
INTER_ROW_PAUSE_SECONDS: float = float(os.getenv("INTER_ROW_PAUSE_SECONDS", "8"))
MAX_RETRIES: int = 5
RETRY_BASE_DELAY: float = 45.0

def build_llm() -> str:
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit(
            "[FATAL] GEMINI_API_KEY not found.\n"
            f"Add it to {_PROJECT_ROOT / '.env'} as:\n"
            "  GEMINI_API_KEY = <your-key>"
        )

    os.environ["GOOGLE_API_KEY"] = api_key

    return GEMINI_MODEL
