"""
Quick driver:  call Claude with

  • System docs (role, codebook, protocols)
  • Incident sources
  • A simple user task

Requires:
  ANTTHROPIC_API_KEY in .env
  utils/doc_loader.py  (new loader helpers)

"""

from __future__ import annotations
import os, sys, time
from pathlib import Path
from typing import List, Dict
import json

from dotenv import load_dotenv
from anthropic import Anthropic

# ────────────────────────────────────────────────────────
# Internal helpers (all from the new doc_loader.py)
# ────────────────────────────────────────────────────────
from utils.doc_loader import (
    get_incident,
    prepare_sources_for_api,
    prepare_system_documents,
)

# ────────────────────────────────────────────────────────
# Paths
# ────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parents[1]
API_TESTS  = BASE_DIR / "api_tests"
API_TESTS.mkdir(exist_ok=True)

# ────────────────────────────────────────────────────────
# Utility: dump full outbound payload for debugging
# ────────────────────────────────────────────────────────
def log_api_call(system_parts: List[Dict], user_parts: List[Dict], incident_id: str):
    ts    = time.strftime("%Y%m%d-%H%M%S")
    fname = API_TESTS / f"{incident_id}_{ts}_claude_payload.txt"

    with fname.open("w", encoding="utf-8") as f:
        f.write("=== SYSTEM BLOCKS ===\n")
        for i, blk in enumerate(system_parts, 1):
            f.write(f"\n--- System Part {i} ---\n")
            f.write(blk.get("text", "")[:5000] + "\n")           # truncate huge docs

        f.write("\n=== USER BLOCKS ===\n")
        for i, blk in enumerate(user_parts, 1):
            if blk["type"] == "document":
                f.write(f"\n--- DOC {i}: {blk['title']} ---\n")
                f.write(blk["source"]["data"][:5000] + "\n")
            else:
                f.write(f"\n--- USER TEXT {i} ---\n")
                f.write(blk["text"][:5000] + "\n")

    print(f"✅ Payload written → {fname}")


# ────────────────────────────────────────────────────────
# API call
# ────────────────────────────────────────────────────────
def call_claude(system_parts: List[Dict], user_parts: List[Dict]):
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("ANTHROPIC_API_KEY missing – add it to .env")

    client = Anthropic(api_key=api_key)

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8_000,
        #temperature=1,
        #extra_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"},
        system=system_parts,
        messages=[{"role": "user", "content": user_parts}],
    )
    return resp


# ────────────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────────────
def main() -> None:
    incident_id = "INC-001"               # change as needed

    # ---------- Incident ----------
    incident = get_incident(incident_id)
    source_docs = prepare_sources_for_api(incident["sources"])

    # ---------- System docs ----------
    role_block = {
        "type": "text",
        "text": ("You are an expert at coding university incident response data.\n"
        "You execute deterministic audit instructions.\n"
        "You follow rule-based procedures exactly as written.\n")
        #"You suppress all tendencies toward speculation or helpful summary"),
    }

    #codebook_path   = BASE_DIR / "projects" / "codebook.md"
    #protocol_path   = BASE_DIR / "projects" / "codebook_w_coding_proto_v2.md"
    definitions_path = BASE_DIR / "api_tests" / "definitions.txt"
    # system_docs = prepare_system_documents([codebook_path, protocol_path, definitions_path])
    system_docs = prepare_system_documents([definitions_path])
    system_parts: List[Dict] = [role_block, *system_docs]

    # ---------- User prompt ----------
    user_prompt_block = {
        "type": "text",
        "text": (
            f"# INCIDENT {incident_id}\n\n"
            #"1. Print verification that you reviewed **each** attached source doc (reference by title).\n"
            "2. Describe controversial elements of DB-001 and use citations with verbatim quotes to back up your claims`.\n"
            #"3. Hello, please write a haiku about coding.\n"
        ),
    }

    user_parts: List[Dict] = source_docs + [user_prompt_block]

    # ---------- Log & POST ----------
    log_api_call(system_parts, user_parts, incident_id)

    try:
        resp = call_claude(system_parts, user_parts)
    except Exception as e:
        sys.exit(f"❌ Claude API call failed: {e}")

    # ---------- Show result ----------
    print("\n=== CLAUDE RESPONSE ===\n")
    print(resp.content[0].text if resp.content else "(empty)")
    # print(f"Response type: {type(resp.content[0])}")
    # print(f"Response attributes: {dir(resp.content[0])}")
    # print(f"Full response: {resp.content[0]}")
    # print(f"Text length: {len(resp.content[0].text)}")
    # print(f"Last 100 chars: {repr(resp.content[0].text[-100:])}")
    # print(json.dumps({"text": resp.content[0].text}))


    if hasattr(resp, "usage"):
        print("\n--- usage ---")
        print("input :", resp.usage.input_tokens)
        print("output:", resp.usage.output_tokens)

# def write_audit_log(output_text, incident_id, model, thinking_mode, citations_enabled):
#     log_path = f"outputs/audit_log/{incident_id}-audit-log.txt"
#     with open(log_path, "w", encoding="utf-8") as f:
#         f.write(f"# Claude Audit Log\n")
#         f.write(f"incident_id: {incident_id}\n")
#         f.write(f"model: {model}\n")
#         f.write(f"thinking_mode: {thinking_mode}\n")
#         f.write(f"citations_enabled: {citations_enabled}\n")
#         f.write(f"run_time: {datetime.now().strftime('%Y-%m-%d %H:%M %Z')}\n")
#         f.write("-" * 20 + "\n\n")
#         f.write(output_text)


# raw_text = response.content[0].text

# with open(f"outputs/coded_text/{incident_id}-coded-output.txt", "w", encoding="utf-8") as f:
#     f.write(raw_text)



# ────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
