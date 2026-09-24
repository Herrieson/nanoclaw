import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

def smart_mock(query):
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a local farming expert. Provide a realistic market price for the organic item requested."},
                      {"role": "user", "content": query}]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Market connection error: {str(e)}"

if __name__ == "__main__":
    print(smart_mock(" ".join(sys.argv[1:])))
