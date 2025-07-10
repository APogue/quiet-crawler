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
from dotenv import load_dotenv

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
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable not set. Export your key "
            "before calling claude_api.send()."
        )

    client = anthropic.Anthropic(api_key=api_key)

    # --- 1. Clean payload for Claude API (remove custom metadata) ---
    api_payload = {k: v for k, v in payload.items() if k != "metadata"}

    # --- 2. Fire request ---
    response = client.messages.create(**api_payload)  # type: ignore[arg-type]

    # --- 3. Extract assistant text ----------------------------------------
# Claude API response structure:
# {
#   "id": "msg_...",
#   "type": "message",
#   "role": "assistant",
#   "model": "claude-3-opus-20240229",
#   "content": [
#       { "type": "text", "text": "Claude's reply here..." }
#   ],
#   "usage": {
#       "input_tokens": 1234,
#       "output_tokens": 567
#   },
#   "stop_reason": "end_turn",
#   "stop_sequence": null
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
