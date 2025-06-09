import os
import time
import tiktoken
from dotenv import load_dotenv
from anthropic import Anthropic
from utils.source_reader import prepare_incident_documents_for_api, get_incident_info

# Determine project root based on the script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Point to the existing 'api_tests' directory
API_TESTS_DIR = os.path.join(BASE_DIR, 'api_tests')
os.makedirs(API_TESTS_DIR, exist_ok=True)

def log_system_and_content_to_file(system_content, user_content, incident_id, suffix="claude_api_call.txt"):
    """
    Logs both system and user content to a file in the api_tests/ directory.
    """
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{incident_id}_{timestamp}_{suffix}"
    file_path = os.path.join(API_TESTS_DIR, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("=== SYSTEM MESSAGE ===\n")
        f.write(f"Number of system parts: {len(system_content)}\n")
        for i, part in enumerate(system_content):
            f.write(f"Part {i+1}: {part.get('text', 'N/A')[:100]}...\n")
        f.write("\n=== USER CONTENT ===\n")
        f.write(f"Number of documents: {len([item for item in user_content if item.get('type') == 'document'])}\n")
        f.write(f"Text instructions: {[item.get('text', 'N/A') for item in user_content if item.get('type') == 'text']}\n")
    
    print(f"✅ API call logged to {file_path}")

def call_claude_api(system_content, user_content):
    """
    Calls the Claude API with system content list and mixed user content (documents + text).
    """
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    client = Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-opus-4-20250514",
        max_tokens=2000,
        temperature=0,
        # Add beta header for 1-hour cache
        extra_headers={"anthropic-beta": "extended-cache-ttl-2025-04-11"},
        system=system_content,  # List of content objects
        messages=[
            {
                "role": "user",
                "content": user_content
            }
        ]
    )

    print("=== API CALL START ===")
    print(response.content[0].text if response.content else "No content")
    print("=== API CALL END ===")
    
    return response

def main():
    incident_id = 'INC-001'  # Example test incident ID

    try:
        # Get incident info and prepare documents
        incident_info = get_incident_info(incident_id)
        documents = prepare_incident_documents_for_api(incident_id)
        
        print(f"Incident: {incident_info['summary']}")
        print(f"Sources loaded: {[doc['title'] for doc in documents]}")
        
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ {e}")
        return

    # Your codebook content (placeholder - replace with actual content)
    codebook_content = """
    PLACEHOLDER CODEBOOK CONTENT:
    
    SEVERITY_SCALE:
    1 = Minor policy concern
    2 = Moderate violation requiring response
    3 = Serious incident with campus-wide impact
    4 = Major crisis requiring immediate intervention
    
    ADMINISTRATIVE_RESPONSE_TIMING:
    - immediate (within 24 hours)
    - prompt (within 1 week)
    - delayed (beyond 1 week)
    - none (no documented response)
    
    [TODO: Replace with actual field_definitions.yml content]
    """

    # Build system message as list of content objects
    system_content = [
        {
            "type": "text",
            "text": "You are an expert at coding university incident response data. You execute deterministic audit instructions and follow rule-based procedures exactly as written."
        },
        {
            "type": "text", 
            "text": codebook_content,
            "cache_control": {
                "type": "ephemeral",
                "ttl": "1h"  # 1-hour cache for codebook
            }
        },
        {
            "type": "text",
            "text": "Apply these definitions consistently. Always cite sources using document titles. You must suppress all tendencies toward speculation or helpful summary."
        }
    ]

    # Build user content: documents + text instruction
    user_content = documents + [
        {
            "type": "text",
            "text": f"""# INCIDENT ID: {incident_id}

## TASK:

Your first task is to print verification that you have reviewed each source document by title.

Your second task is to print the exact text content of source SOC-003 as provided in the documents.

You MUST NOT summarize or paraphrase. You MUST return the text exactly as provided.

Your third task is to code this incident according to the established protocol and output structured YAML."""
        }
    ]

    # Log the API call structure
    log_system_and_content_to_file(system_content, user_content, incident_id)

    # Call the API
    try:
        api_response = call_claude_api(system_content, user_content)
        
        # Print usage stats
        if hasattr(api_response, 'usage'):
            print(f"\n=== USAGE STATS ===")
            print(f"Input tokens: {api_response.usage.input_tokens}")
            print(f"Output tokens: {api_response.usage.output_tokens}")
            if hasattr(api_response.usage, 'cache_creation_input_tokens'):
                print(f"Cache creation tokens: {api_response.usage.cache_creation_input_tokens}")
            if hasattr(api_response.usage, 'cache_read_input_tokens'):
                print(f"Cache read tokens: {api_response.usage.cache_read_input_tokens}")

    except Exception as e:
        print(f"❌ API call failed: {e}")
        return

    print("\n=== API RESPONSE CONTENT ===")
    if api_response.content:
        print(api_response.content[0].text)

if __name__ == "__main__":
    main()