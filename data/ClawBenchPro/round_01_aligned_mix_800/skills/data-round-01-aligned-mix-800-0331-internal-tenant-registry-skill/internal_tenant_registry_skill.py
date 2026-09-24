import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def internal_registry_query(query):
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are the Internal Tenant Registry system. Return a brief summary for the requested tenant based on the context of 'The Arches' complex. If asked about T002 or T004, mention they have a history of late payments in Q3."},
                {"role": "user", "content": query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Database Connection Error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(internal_registry_query(" ".join(sys.argv[1:])))
