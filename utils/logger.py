# =========================================================
# utils/logger.py
# ---------------------------------------------------------
"""
logger.py
---------
Audit logger for Quiet-Crawler pipeline.

Produces **two** artefacts per Claude run using a run‑specific identifier:

1. `<run_name>-input.json`   – full request payload (debugging/replay)
2. `<run_name>-response.txt` – readable audit log containing
   • metadata (model, thinking_mode, etc.)
   • Claude completion (or pretty JSON fallback)
   • timestamp + link to matching input file
"""

from __future__ import annotations

import json
import datetime as _dt
from pathlib import Path
from typing import Any, Dict

from utils.path_manager import get_audit_log_dir

_TIMESTAMP_FMT = "%Y-%m-%d %H:%M UTC"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now() -> str:
    """UTC timestamp in human‑readable form."""
    return _dt.datetime.utcnow().strftime(_TIMESTAMP_FMT)


def _build_filename(incident_id: str, run_name: str, suffix: str, ext: str) -> Path:
    """Return `outputs/audit_log/incident_id/<run_name>-<suffix>.<ext>`."""
    dir_path = get_audit_log_dir(incident_id)
    safe_name = run_name.replace(" ", "_")
    return dir_path / f"{safe_name}-{suffix}.{ext}"

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def log_payload(run_name: str, payload: Dict[str, Any]) -> Path:
    """Persist full input payload as prettified JSON."""
    incident_id = payload.get("metadata", {}).get("incident_id", "unknown")
    if not incident_id:
        raise ValueError("Missing `incident_id` in payload metadata – cannot log output.")
    path = _build_filename(incident_id, run_name, "input", "json")
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def log_response(
    run_name: str,
    output_text: str,
    *,
    payload: Dict[str, Any],
) -> Path:

    """Write a concise human‑readable audit file with metadata + output."""
    incident_id = payload.get("metadata", {}).get("incident_id", "unknown")
    if not incident_id:
        raise ValueError("Missing `incident_id` in payload metadata – cannot log output.")
    path = _build_filename(incident_id, run_name, "response", "txt")

    # ------------------------------------------------------------------
    # Extract metadata from payload (if supplied)
    # ------------------------------------------------------------------
    metadata = {
        "incident_id": payload.get("metadata", {}).get("incident_id"),
        "model": payload.get("model"),
        "thinking_mode": payload.get("metadata", {}).get("thinking_mode"),
        "citations_enabled": payload.get("metadata", {}).get("citations_enabled"),
    }

    # ------------------------------------------------------------------
    # Write out audit log
    # ------------------------------------------------------------------
    with path.open("w", encoding="utf-8") as f:
        f.write("# Claude Audit Log\n")
        f.write(f"incident_id: {metadata['incident_id']}\n")
        f.write(f"model: {metadata['model']}\n")
        f.write(f"thinking_mode: {metadata['thinking_mode']}\n")
        f.write(f"citations_enabled: {metadata['citations_enabled']}\n")
        f.write(f"run_time: {_now()}\n")
        f.write("-" * 20 + "\n\n")
        f.write(output_text.strip())
        f.write("\n\n")
        f.write(f"(See input payload: {str(_build_filename(incident_id, run_name, 'input', 'json'))})\n")

    return path


def log(run_name: str, payload: Dict[str, Any], raw_response: str | Dict[str, Any]):
    """Convenience wrapper logging both payload and response."""
    log_payload(run_name, payload)
    log_response(run_name, raw_response, payload=payload)
