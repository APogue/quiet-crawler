import os
import time
import tiktoken
from dotenv import load_dotenv
from anthropic import Anthropic
from utils.source_reader import (
    get_sources_for_incident,
    verify_source_ids_exist,
    prepare_sources_for_prompt
)

# Determine project root based on the script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Point to the existing 'api_tests' directory
API_TESTS_DIR = os.path.join(BASE_DIR, 'api_tests')
os.makedirs(API_TESTS_DIR, exist_ok=True)

def log_prompt_to_file(prompt, incident_id, suffix="claude_api_prompt.txt"):
    """
    Logs the prompt to a file in the api_tests/ directory.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{incident_id}_{timestamp}_{suffix}"
    file_path = os.path.join(API_TESTS_DIR, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"✅ Prompt saved to {file_path}")


# Placeholder: Function to call the Claude API (replace with real call)
def call_claude_api(prompt):

    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        # array (list) of message objects, each of which is a dict
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

    # Get relevant source IDs
    source_ids = get_sources_for_incident(incident_id)
    print(f"Sources for incident {incident_id}: {source_ids}")

    # Validate that sources exist in both filesystem and master metadata
    missing_files, missing_metadata = verify_source_ids_exist(source_ids)
    if missing_files:
        print(f"⚠️ Missing source files: {missing_files}")
    if missing_metadata:
        print(f"⚠️ Missing source metadata in source_master.yml: {missing_metadata}")
    if missing_files or missing_metadata:
        print("❌ Cannot proceed until missing files and metadata are fixed.")
        return


    # Prepare the source text block for the prompt
    source_text_block = prepare_sources_for_prompt(source_ids)

    # Build the prompt for Claude, this is a single string
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
    # Save the prompt before calling the API, if prompt includes system message this needs to be changed
    log_prompt_to_file(prompt, incident_id, suffix="claude_api_prompt.txt")

    # Count tokens, want to stay under 100k
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(prompt)
    print(f"Approximate token count: {len(tokens)}")
    
    # Call the API (placeholder function)
    api_response = call_claude_api(prompt)

    # Print or save the response
    print("\n=== API RESPONSE ===")
    print(api_response)

if __name__ == "__main__":
    main()







