import os
import sys
import httpx
from openai import OpenAI

def search_policy(query):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Hospital Policy Database. If asked about Heparin Floor Threshold, return 'The current safety floor stock threshold for Heparin is 25,000 units per shift. Any usage above this requires a Chief Nursing Officer flag.'"},
                {"role": "user", "content": query}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except:
        return "Internal Policy Server Error 500."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(search_policy(sys.argv[1]))
