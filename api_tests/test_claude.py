import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

long_document = """
This is a sample document that you want Claude to reference.
It can be very long, multiple paragraphs. Each sentence will be chunked for citations.
"""

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
                        "data": long_document
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

print(response.content)
