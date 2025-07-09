#!/usr/bin/env python
"""
run_pass1_condense_policy.py
============================

Condense a single policy source (POL-### or PHIL-###) for a given
incident and save the summary into `outputs/condensation/<INC-ID>/`.

The file name is built from the *exact* `run_name` returned by
`utils.test_claude.send_prompt()`, ensuring it lines up with the
matching input / response audit-log files :

    outputs/audit_log/INC-001/INC-001-policy-POL-003-input.json
    outputs/audit_log/INC-001/INC-001-policy-POL-003-response.txt
    outputs/condensation/INC-001/INC-001-policy-POL-003-condensed.txt

Usage
-----
python -m pipeline.run_pass1_condense_policy \
       --incident-id INC-001 \
       --source-id  POL-003 \
       --model      claude-3-opus
       [--dry-run]          # skips the API call, logs input only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from utils import preprocess_payload, test_claude
from utils.path_manager import get_condensation_dir


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:  # pragma: no cover
    parser = argparse.ArgumentParser(
        prog="run_pass1_condense_policy",
        description="Condense a single POL-/PHIL- policy file via Claude.",
    )
    parser.add_argument(
        "-i", "--incident-id",
        required=True,
        help="Incident identifier, e.g. INC-001",
    )
    parser.add_argument(
        "-s", "--source-id",
        required=True,
        help="Policy source ID, e.g. POL-003 or PHIL-005",
    )
    parser.add_argument(
        "--model",
        default="claude-3-opus",
        help="Claude model name (default: claude-3-opus)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log the payload but do NOT send the request to Claude.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def main() -> None:  # pragma: no cover
    args = _parse_args()

    # 1️⃣  Build Claude payload ------------------------------------------------
    system, messages = preprocess_payload.build_policy_condense_prompt(args.source_id)
    payload: dict = {
        "model": args.model,
        "max_tokens": 3000,
        "temperature": 0.2,  # conservative, focused on structure
        "system": system,
        "messages": messages,
        "metadata": {
            "incident_id": args.incident_id,
            "phase": f"policy-{args.source_id}",
        },
    }

    # 2️⃣  Send to Claude (or skip if --dry-run) -------------------------------
    completion, run_name = test_claude.send_prompt(
        payload,
        dry_run=args.dry_run,
    )

    # Dry-run stops here (payload + run_name already logged by test_claude)
    if args.dry_run:
        print("[DRY-RUN] Payload logged – no API request sent.")
        print(f"[DRY-RUN] Would have written condensation file for run: {run_name}")
        return

    # 3️⃣  Persist the condensed summary --------------------------------------
    condensation_dir: Path = get_condensation_dir(args.incident_id)
    out_path: Path = condensation_dir / f"{run_name}-condensed.txt"
    out_path.write_text(completion, encoding="utf-8")

    print(f"[OK] Condensed summary written → {out_path.relative_to(Path.cwd())}")


# ---------------------------------------------------------------------------

if __name__ == "__main__":  # pragma: no cover
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nInterrupted by user")
