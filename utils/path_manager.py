# utils/path_manager.py
"""
Centralized path definitions and helpers for Quiet-Crawler.

This module defines base paths and provides reusable functions for
constructing consistent, incident-aware file locations across the pipeline.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Base directory resolution
# ---------------------------------------------------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent
SOURCES_DIR: Path = BASE_DIR / "sources"
INCIDENT_DATA_PATH: Path = BASE_DIR / "_data" / "incident_data.yml"

# ---------------------------------------------------------------------------
# Audit log paths (Pass 1 + Pass 2)
# ---------------------------------------------------------------------------
def get_audit_log_dir(incident_id: str) -> Path:
    path = BASE_DIR / "outputs" / "audit_log" / incident_id
    path.mkdir(parents=True, exist_ok=True)
    return path

# ---------------------------------------------------------------------------
# Condensation output paths (Pass 1)
# ---------------------------------------------------------------------------
def get_condensation_dir(incident_id: str) -> Path:
    path = BASE_DIR / "outputs" / "condensation" / incident_id
    path.mkdir(parents=True, exist_ok=True)
    return path


