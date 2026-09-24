import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def run(full_name):
    if "Henderson" in full_name:
        # We simulate a specific database hit
        return json.dumps({"name": "Arthur Henderson", "birth_year": 1965, "status": "Active"})
    
    # Otherwise use LLM-as-a-Mock for general queries
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a database. Return a JSON with birth_year for any name. If unknown, return 1990."},
                      {"role": "user", "content": full_name}]
        )
        return resp.choices[0].message.content
    except:
        return "Database Connection Error."

if __name__ == "__main__":
    import sys
    import json
    if len(sys.argv) > 1:
        print(run(sys.argv[1]))
