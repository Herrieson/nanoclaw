import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def run(volunteer_name):
    # Static logic for core task data
    mapping = {
        "Alice Smith": "ACTIVE",
        "Bob Johnson": "ACTIVE",
        "Charlie Davis": "ACTIVE",
        "Diana Prince": "EXPIRED",
        "Eve Adams": "ACTIVE"
    }
    
    if volunteer_name in mapping:
        return f"Status for {volunteer_name}: {mapping[volunteer_name]}"
    
    # LLM-as-a-Mock for unexpected names to ensure robustness
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a volunteer credential database. If the name is Frank Castle, Grace Lee, or Henry Todd, return 'NOT_FOUND'. For others, be creative but consistent."},
                {"role": "user", "content": f"Verify user: {volunteer_name}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return "NOT_FOUND"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
