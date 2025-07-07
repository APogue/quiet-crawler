# ============================================================
# run_pass1_condense_policy.py
# ------------------------------------------------------------
"""
Pipeline ‑ Pass 1: Condense a single policy / guidance document
================================================================

This runner takes a *policy source ID* (e.g. "POL-017" or "PHIL-002")
from the `sources/` directory, sends it to Claude with the
**policy‑condense prompt** (see `utils.preprocess_payload.build_policy_condense_prompt`),
and writes two audit artefacts:

1. `outputs/audit_log/<run_name>-input.json`    – full payload
2. `outputs/audit_log/<run_name>-response.txt` – Claude summary text

It is intentionally single‑document / single‑run so that you can inspect
and tweak the prompt until condensation output is exactly what you need
for Pass 2. Later, you can batch‑wrap this script or extend it to loop
through all POL‑/PHIL‑ source IDs.

Example
-------
```bash
python -m pipeline.run_pass1_condense_policy POL-003 --model claude-sonnet-4-20250514
```

CLI Arguments
-------------
`policy_id` (positional)   – Source ID to process (must exist in `sources/`)
`--model`                  – Claude model name (default: claude-sonnet-4-20250514)
`--dry`                    – Build & log payload but *do not* call Claude
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from utils.preprocess_payload import build_policy_condense_prompt
from utils import test_claude  # Wrapper that logs + sends

# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Condense one policy document with Claude")
    parser.add_argument("policy_id", help="Source ID of the policy (e.g. POL-017)")
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-20250514",
        help="Claude model name (default: %(default)s)",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        help="Build and log payload but skip Claude API call",
    )
    return parser.parse_args()

# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    args = _parse_args()

    # ---------- 1. Build messages array ----------
    messages = build_policy_condense_prompt(args.policy_id)

    # Claude ChatCompletion payload structure
    # • Pass 1 does *not* attach external documents; everything is inline
    payload: Dict[str, Any] = {
        "model": args.model,
        "messages": messages,
        "max_tokens": 4096,  # Tweaked for long policies
        # Metadata is passed through to logger for file‑naming
        "metadata": {
            "incident_id": args.policy_id,  # Re‑using for convenience
            "phase": "policy-condense",
            "thinking_mode": "chain_of_thought",  # Optional
            "citations_enabled": False,
        },
    }

    # ---------- 2. Send (or dry‑run) ----------
    summary_text = test_claude.send_prompt(payload, dry_run=args.dry)

    if args.dry:
        print("[DRY‑RUN] Payload logged; Claude call skipped.")
    else:
        print("\n=== Claude Condensation Output ===\n")
        # Guard: send_prompt returns None when dry_run=True
        print(summary_text or "<empty response>")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
