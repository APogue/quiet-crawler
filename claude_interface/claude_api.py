# =========================================================
# claude_api.py  (adapter layer)
# ---------------------------------------------------------
"""
Minimal Claude API adapter for Quiet‑Crawler.

• Reads API key from the environment variable **ANTHROPIC_API_KEY**
• Sends a fully‑formed *payload* dict (built elsewhere) to the Anthropic Chat Completions endpoint (v2023‑06‑01 or v2023‑06‑01-preview‑beta).
• Normalises the response to a simple structure expected by *test_claude.py*:
    {
        "completion": <assistant text output>,
        "raw_response": <full JSON response from Anthropic>
    }

Only responsibility: convert payload ↔ HTTP(SDK) response.  No logging, no
file I/O, no retries (caller can wrap if needed).
"""

from __future__ import annotations

import os
from typing import Any, Dict

try:
    import anthropic  # Official Anthropic SDK (pip install anthropic)
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "anthropic SDK not found. Install with `pip install anthropic` or "
        "provide your own client implementation."
    ) from exc



# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def send(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Send *payload* to the Claude API via Anthropic SDK.

    Parameters
    ----------
    payload : dict
        A dict containing at minimum:
          - "model": model name (e.g. "claude-3-opus")
          - "messages": List[Dict] OR (for older API versions) "system"/"user" parts
        Any additional supported keys (e.g., "temperature", "max_tokens") are
        forwarded verbatim.

    Returns
    -------
    dict
        ``{"completion": text, "raw_response": response_dict}``
        where *text* is the assistant's first text block.
    """
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

    _ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    if not _ANTHROPIC_API_KEY:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable not set. Export your key "
            "before calling claude_api.send()."
        )

    _client = anthropic.Anthropic(api_key=_ANTHROPIC_API_KEY)
    
    # --- 1. Fire request ---------------------------------------------------
    response = _client.messages.create(**payload)  # type: ignore[arg-type]

    # --- 2. Extract assistant text ----------------------------------------
    # Anthropic response structure:
    # {
    #   "id": "...",
    #   "role": "assistant",
    #   "content": [ {"type": "text", "text": "..."} ],
    #   ...
    # }
    try:
        first_block = response.content[0]
        if first_block.type != "text":  # pragma: no cover
            raise ValueError("First content block is not text – unsupported format.")
        completion_text = first_block.text
    except (AttributeError, IndexError) as exc:  # pragma: no cover
        raise RuntimeError("Unexpected response structure from Claude API") from exc

    # --- 3. Return normalised dict ----------------------------------------
    return {
        "completion": completion_text,
        "raw_response": response,
    }
