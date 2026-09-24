import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def resolve_user(user_id):
    # Logic: Only U001 is missing from local.
    if user_id == "U001":
        return json.dumps({"id": "U001", "name": "Arjun Mehta"})
    
    # Fallback to LLM for other queries to simulate a real API
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a user database API. If user_id is U005 return Amit Patel. Else return User Not Found."}],
            temperature=0
        )
        return resp.choices[0].message.content
    except:
        return "Internal API Error"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(resolve_user(sys.argv[1]))
