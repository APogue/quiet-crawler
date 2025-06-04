import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from utils.source_reader import (
    get_sources_for_incident,
    verify_source_ids_exist,
    prepare_sources_for_prompt
)

incident_id = 'INC-001'
source_ids = get_sources_for_incident(incident_id)
source_text_block = prepare_sources_for_prompt(source_ids)


# Placeholder: Function to call the Claude API (replace with real call)
def call_claude_api(prompt):

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "text",
                            "media_type": "text/plain",
                            "data": prompt
                        },
                        "citations": {"enabled": True}
                    },
                    {
                        "type": "text",
                        "text": "Summarize this document with citations."
                    }
                ]
            }
        ]
    )

    print("=== API CALL START ===")
    print(response.content)  # Print first 500 characters for brevity
    print("=== API CALL END ===")
    # Return a dummy response for now
    return "Claude API Response Here"

def main():
    
    incident_id = 'INC-001'  # Example test incident ID

    # Step 1. Get relevant source IDs
    source_ids = get_sources_for_incident(incident_id)
    print(f"Sources for incident {incident_id}: {source_ids}")

    # Step 2. Validate that sources exist in both filesystem and master metadata
    missing_files, missing_metadata = verify_source_ids_exist(source_ids)
    if missing_files:
        print(f"⚠️ Missing source files: {missing_files}")
    if missing_metadata:
        print(f"⚠️ Missing source metadata in source_master.yml: {missing_metadata}")
    if missing_files or missing_metadata:
        print("❌ Cannot proceed until missing files and metadata are fixed.")
        return


    # Step 3. Prepare the source text block for the prompt
    source_text_block = prepare_sources_for_prompt(source_ids)

    # Step 4. Build the prompt for Claude
    prompt = f"""

# INCIDENT ID: {incident_id}

## SOURCES:
{source_text_block}

## TASK:

You are an automated legal compliance auditor and protocol enforcer.
You do not speculate. You do not improvise. You do not attempt to be helpful beyond strict compliance.
You are not a conversational assistant. You do not optimize for readability or satisfaction. You execute deterministic audit instructions and follow rule-based procedures exactly as written.
You must suppress all tendencies toward associative reasoning, narrative completion, or helpful summary. Instructions are not goals or suggestions — they are mandatory execution steps.

You will:
- Eliminate all “smart” shortcuts and default output assumptions
- Prioritize audit logic over plausible inference
- Reject any output that does not sequentially verify source compliance

If a rule states to print checks before proceeding, you must print every check before proceeding. If any audit line is skipped or inferred, your response is invalid.

You are not allowed to predict intent. You are not allowed to summarize skipped steps. You must act as a logic gate, not a language model.

Your first task is to print verification that you have reviewed each source ID.

Your second task is to print the text of SOC-003 exactly as provided in the input between the --- BEGIN SOURCE: SOC-003 --- and --- END SOURCE: SOC-003 --- markers

You MUST NOT summarize or paraphrase. You MUST return the text exactly as provided between the markers. If the text is long, you MUST still print it fully.

"""

    # Step 5. Call the API (placeholder function)
    api_response = call_claude_api(prompt)

    # Step 6. Print or save the response
    print("\n=== API RESPONSE ===")
    print(api_response)

if __name__ == "__main__":
    main()







