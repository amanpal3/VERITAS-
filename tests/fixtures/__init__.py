"""
VERITAS - Test Fixtures Package
Provides deterministic integration fixtures for cross-member test scenarios.
"""
from pathlib import Path
import json

FIXTURES_DIR = Path(__file__).resolve().parent
HANDOFF_SCENARIO_PATH = FIXTURES_DIR / "handoff_scenario.json"


def load_handoff_scenario() -> dict:
    """Loads raw dictionary payload of the canonical handoff scenario."""
    with open(HANDOFF_SCENARIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
