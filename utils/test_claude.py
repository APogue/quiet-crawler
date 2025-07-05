# =========================================================
# utils/test_claude.py
# ---------------------------------------------------------
"""
test_claude.py
--------------
Wrapper utility that couples three jobs into one convenient call:

1. ✅  Audit-log the outbound *payload* via `logger.log_payload()`
2. 🚀  Send the request to Claude using `claude_api.send()`
3. 📝  Audit-log Claude's *raw* response with metadata and timestamp
4. 🔁  Return only the `completion` string (for saving or parsing)

Generates two files per run using a run-specific identifier:
- `<run_name>-input.json`
- `<run_name>-response.txt`
"""

from __future__ import annotations

from typing import Any, Dict
import traceback
from datetime import datetime

from utils import logger

try:
    import claude_api  # Must live at repo root
except ModuleNotFoundError as exc:  # pragma: no cover
    raise ImportError(
        "claude_api.py not found in PYTHONPATH – run scripts from repo root."
    ) from exc

# ---------------------------------------------------------------------------
# Run name generator (used for syncing payload + response logs)
# ---------------------------------------------------------------------------

def generate_run_name(payload: dict) -> str:
    incident_id = payload.get("metadata", {}).get("incident_id", "unknown")
    phase = payload.get("metadata", {}).get("phase", "run")
    model = payload.get("model", "claude-unknown").replace("claude-", "").replace("3-", "").replace("_", "-")
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%MZ")
    return f"{incident_id}-{phase}-{model}-{timestamp}"

# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def send_prompt(payload: Dict[str, Any], *, dry_run: bool = False) -> str | None:
    """
    Main runner: logs payload, sends to Claude (unless dry), logs response.

    Parameters
    ----------
    payload : dict
        Full Claude request body (must include metadata.incident_id and model)
    dry_run : bool, default False
        If True, logs input but skips the Claude API call

    Returns
    -------
    str | None
        Claude's `completion` string, or None if dry_run=True
    """
    run_name = generate_run_name(payload)
    logger.log_payload(run_name, payload)

    if dry_run:
        return None

    try:
        result: Dict[str, Any] = claude_api.send(payload)
    except Exception:
        tb = traceback.format_exc()
        logger.log_response(run_name, f"[ERROR]\n{tb}", payload=payload)
        raise

    logger.log_response(run_name, result, payload=payload)
    return result.get("completion")


# ---------------------------------------------------------------------------
# CLI testing stub
# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    import json, sys
    from pathlib import Path

    if len(sys.argv) != 2:
        print("Usage: python -m utils.test_claude <payload.json>")
        sys.exit(1)

    payload_path = Path(sys.argv[1])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    result = send_prompt(payload)
    print("--- Claude completion ---\n")
    print(result)
