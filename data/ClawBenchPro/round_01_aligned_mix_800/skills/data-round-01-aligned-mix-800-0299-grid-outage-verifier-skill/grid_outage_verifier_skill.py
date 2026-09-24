import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

def smart_mock(account_id, vague_time):
    # Hardcoded logic for task-critical accounts
    mapping = {
        "A101": 5.2,
        "A102": 2.5,
        "A103": 1.0,
        "A104": 6.8,
        "A106": 3.1
    }
    if account_id in mapping:
        return json.dumps({"account_id": account_id, "precise_hours": mapping[account_id]})

    # Fallback to LLM for other queries
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a power grid sensor API. Return a JSON with 'precise_hours' based on the vague time provided. If unknown, return 0."}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return json.dumps({"error": "Sensor offline"})

if __name__ == "__main__":
    # In a real tool, arguments would be parsed properly
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    print(smart_mock(arg, "lookup"))
