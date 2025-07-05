"""
preprocess_payload.py
---------------------
Build Claude-ready `messages` / `documents` blocks for both stages
of the Quiet-Crawler pipeline.

Public helpers
==============
- build_policy_condense_prompt(source_id)          -> List[Dict]   (Pass 1)
- build_incident_coding_parts(incident_id, ...)    -> Tuple[List[Dict], List[Dict]]  (Pass 2)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple, Dict

from utils.doc_loader import (
    BASE_DIR,
    get_incident,
    load_source_content,
    prepare_sources_for_api,
    prepare_system_documents,
)

# ---------------------------------------------------------------------------
# Internal: default system files (loaded once, reused for every incident run)
# ---------------------------------------------------------------------------

_SYSTEM_DIR: Path = BASE_DIR / "inputs" / "system"

_DEFAULT_SYSTEM_FILES: List[Path] = [
    _SYSTEM_DIR / "system_role.txt",
    _SYSTEM_DIR / "definitions.txt",
    _SYSTEM_DIR / "justification_protocol.txt",
    _SYSTEM_DIR / "codebook_w_coding_proto_v2.md",
    _SYSTEM_DIR / "coding_workflow.txt", # this is a user message, not system
]

# ---------------------------------------------------------------------------
# Pass 1 : policy-document condensation
# ---------------------------------------------------------------------------


def build_policy_condense_prompt(source_id: str) -> List[Dict]:
    """
    Craft a minimal messages array for Claude that asks it to extract rule
    structure from a *single* policy / guidance document (POL- or PHIL-).

    Returns
    -------
    List[Dict]
        Suitable for the `messages` field in a ChatCompletion call.
    """
    policy_text = load_source_content(source_id)
    return [
        {
            "role": "user",
            "content": (
                "You are an institutional-policy summarizer.\n"
                "Extract enforceable RULES, thresholds, and ambiguous-enforcement language "
                "from the following document. Output a clean, section-based summary that "
                "retains original clause numbering where available.\n\n"
                f"SOURCE ID: {source_id}\n\n"
                "----- BEGIN POLICY TEXT -----\n"
                f"{policy_text}\n"
                "----- END POLICY TEXT -----"
            ),
        }
    ]


# ---------------------------------------------------------------------------
# Pass 2 : incident coding
# ---------------------------------------------------------------------------


def _default_system_parts() -> List[Dict]:
    """Load core system-level reference files. The same for every incident. Shared config."""
    # system_role.txt is already a plain-text persona — no need for extra wrapping
    return prepare_system_documents(_DEFAULT_SYSTEM_FILES)


def build_incident_coding_parts(
    incident_id: str, extra_system_paths: List[Path] | None = None
) -> Tuple[List[Dict], List[Dict]]:
    """
    Build *(system_parts, user_parts)* for the main incident-coding Claude call.

    Parameters
    ----------
    incident_id : str
        e.g. "INC-001"
    extra_system_paths : list[pathlib.Path], optio/nal
        Any additional system docs (dynamic inputs) to append (e.g. freshly condensed policy summaries).

    Returns
    -------
    Tuple[List[Dict], List[Dict]]
        system_parts → goes into the `messages` array (system role + static refs)
        user_parts   → source documents + user instruction (will be split into
                       `documents` and a trailing text item by the caller)
    """
    incident = get_incident(incident_id)

    # ---------- Claude system section ----------
    system_parts: List[Dict] = _default_system_parts()
    if extra_system_paths:
        system_parts += prepare_system_documents(extra_system_paths)

    # ---------- Claude user section ----------
    source_docs = prepare_sources_for_api(incident["sources"])

    user_prompt_block = {
        "type": "text",
        "text": (
            f"# INCIDENT {incident_id}\n\n"
            "Using ONLY the attached sources and rulebooks, execute the coding_workflow "
            "step-by-step and output one <justification> YAML block per variable.\n"
            "Do not provide narrative summary outside XML tags."
        ),
    }

    user_parts: List[Dict] = source_docs + [user_prompt_block]
    return system_parts, user_parts
