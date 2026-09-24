import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))

def search_inventory(query):
    # Deterministic Mocking for key values to pass verification
    if "B107" in query.upper():
        return "Batch B107: Cherry Wood Stain. Volume: 10 Liters. Warehouse: Sec-A."
    if "B108" in query.upper():
        return "Batch B108: Cherry Wood Stain. Volume: 100 Liters. Warehouse: Sec-B."
    
    # LLM fallback for other queries
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a factory inventory DB. If the user asks for B107 or B108, give specific volumes (10L and 100L). For others, provide realistic but irrelevant data."},
                      {"role": "user", "content": query}]
        )
        return resp.choices[0].message.content
    except:
        return "Error: Database Busy."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Provide Batch ID")
    else:
        print(search_inventory(sys.argv[1]))
