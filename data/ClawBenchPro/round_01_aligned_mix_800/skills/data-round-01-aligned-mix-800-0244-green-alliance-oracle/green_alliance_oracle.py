import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "https://api.openai.com/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def search_oracle(query):
    # Specialized logic for the task: EQ-555 is Green
    if "EQ-555" in query:
        return "The Green Alliance confirms: EQ-555 (Hydrogen Fuel Cell Gen-Z) is certified as a 'Green' high-efficiency asset as of last quarter."
    
    # Generic LLM fallback
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are the Green Alliance Oracle. Verify equipment categories."},
                      {"role": "user", "content": query}]
        )
        return resp.choices[0].message.content
    except:
        return "Search Service Temporarily Unavailable."

if __name__ == "__main__":
    import sys
    print(search_oracle(" ".join(sys.argv[1:])))
