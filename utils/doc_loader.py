# doc_loader.py
"""
Scoped to raw sources and incident metatdata loading
====================================================
Unified helpers for loading incident *sources* **and** static *system* documents
into Claude‑compatible payloads.

Key functions
-------------
- get_incident(incident_id) → Dict       | fetch + validate one incident record
- prepare_sources_for_api(source_ids)    | convert incident sources to "document" blocks
- prepare_system_documents(file_paths)   | convert files (codebook, protocols) to "text" blocks

Notes on path handling
----------------------
* Always build file paths with **absolute** Path objects – easiest is
  BASE_DIR / "subdir" / "file.ext".  This avoids surprises when the
  working directory changes (e.g. when running scripts from different
  places or via python -m).
* The helper functions assume UTF‑8 encoded text files.

This module supersedes the older source_reader.py so that the utilities
cover both incident sources **and** static documentation.
"""

from __future__ import annotations  # Post‑poned evaluation of type hints (safe for 3.8+)

from functools import lru_cache
from pathlib import Path
from typing import List, Dict
import yaml

# -----------------------------------------------------------
# Path configuration
# -----------------------------------------------------------
# Resolve BASE_DIR one level up from this file (…/quiet-crawler/)
BASE_DIR: Path = Path(__file__).resolve().parent.parent

SOURCES_DIR: Path = BASE_DIR / "sources"
INCIDENT_DATA_PATH: Path = BASE_DIR / "_data" / "incident_data.yml"

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

@lru_cache()
def _incident_table() -> List[Dict]:
    """Parse *incident_data.yml* exactly once per Python process.

    Returns
    -------
    List[Dict]
        Parsed list of incident‑record dictionaries.

    The cache is cleared automatically when the interpreter exits.
    Call _incident_table.cache_clear() manually if the YAML file
    is edited during runtime and needs to be re‑loaded.
    """
    try:
        data = yaml.safe_load(INCIDENT_DATA_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Incident data file not found at {INCIDENT_DATA_PATH}"
        ) from exc
    except yaml.YAMLError as exc:
        raise ValueError(
            f"Unable to parse YAML in {INCIDENT_DATA_PATH}: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            f"Expected the YAML root to be a list; got {type(data).__name__}"
        )
    return data


def get_incident(incident_id: str) -> Dict:
    """Return the incident record for *incident_id* and verify that every
    referenced source file exists in the sources/ directory.

    Raises
    ------
    KeyError
        If no incident with the given ID is found.
    FileNotFoundError
        If any listed source files are missing.
    """
    incident = next(
        (row for row in _incident_table() if row.get("id") == incident_id),
        None,
    )
    if incident is None:
        raise KeyError(f"Incident {incident_id!r} not found in {INCIDENT_DATA_PATH}")

    # Ensure each "SID.txt" exists under sources/
    missing = [
        sid
        for sid in incident.get("sources", [])
        if not (SOURCES_DIR / f"{sid}.txt").exists()
    ]
    if missing:
        raise FileNotFoundError(
            f"Missing source files for incident {incident_id}: {missing}"
        )

    return incident

# ---------------------------------------------------------------------------
# Source‑document helpers
# ---------------------------------------------------------------------------

def load_source_content(source_id: str) -> str:
    """Read and return the plaintext content for a single source file.

    Parameters
    ----------
    source_id : str
        Source identifier, e.g. "DB-001" or "SOC-017".

    Returns
    -------
    str
        File contents as Unicode text.

    Raises
    ------
    FileNotFoundError
        If the specified source file does not exist.
    """
    txt_path: Path = SOURCES_DIR / f"{source_id}.txt"
    if not txt_path.exists():
        raise FileNotFoundError(f"Source file not found: {txt_path}")
    return txt_path.read_text(encoding="utf-8")


def prepare_sources_for_api(source_ids: List[str]) -> List[Dict]:
    """Convert incident *source* IDs into Claude‑compatible document blocks.

    Each document dict looks like:
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": "<file contents>"
            },
            "title": "<source id>",
            "citations": {"enabled": True}
        }

    Parameters
    ----------
    source_ids : List[str]
        List of source identifiers to include.

    Returns
    -------
    List[Dict]
        Ready‑to‑upload document objects.
    """
    return [
        {
            "type": "document",
            "source": {
                "type": "text",
                "media_type": "text/plain",
                "data": load_source_content(sid),
            },
            "title": sid,
            "citations": {"enabled": False},
        }
        for sid in source_ids
    ]

# ---------------------------------------------------------------------------
# System‑document helpers
# ---------------------------------------------------------------------------


def prepare_system_documents(file_paths: List[Path]) -> List[Dict]:
    """Convert plaintext / Markdown files into Claude‑compatible text blocks.

    **Path advice**
    --------------
    Callers should pass **absolute** Path objects – or build them with
    BASE_DIR / "..." – to avoid surprises if the current working
    directory changes.

    Parameters
    ----------
    file_paths : List[pathlib.Path]
        Absolute paths to the files you want to embed in the system
        message (e.g., codebook.md, protocols.md, role.txt).

    Returns
    -------
    List[Dict]
        List of Claude‑ready content objects, each of the form
        { "type": "text", "text": "<file contents>" }.
    """
    return [
        {
            "type": "text",
            "text": path.read_text(encoding="utf-8"),
            # Optional helper metadata—remove if you don’t need it:
            "title": path.name,
            #"cache_control": {
              #  "type": "ephemeral",
              #  "ttl": "1h"  # 1-hour cache for codebook
           # }
        }
        for path in file_paths
    ]


# ---------------------------------------------------------------------------
# CLI sanity check (optional)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) <= 2:
        print("Usage: python -m utils.doc_loader <INCIDENT_ID> <FILE_PATH …>")
        print("   or  python utils/doc_loader.py <INCIDENT_ID> <FILE_PATH …>")
        sys.exit(1)

    inc_id = sys.argv[1]
    inc = get_incident(inc_id)
    print(f"Incident {inc_id}: {inc.get('summary', 'No summary provided')}")
    print("Sources:", ", ".join(inc.get("sources", [])))

    # Preview any extra files passed on the command line
    for extra in sys.argv[2:]:
        p = Path(extra)
        if p.exists():
            print(f"--- {p.name} ---\n{p.read_text(encoding="utf-8")[:120]}…\n")
