import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def main():
    query = " ".join(sys.argv[1:])
    
    # LLM-as-a-Mock logic
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    
    prompt = f"The user is searching for: {query}. If they are asking about 'Industrial Safety Supplies Corp' or 'V-99', tell them it's a safety equipment vendor. If they ask about 'Creative Minds', it's art stuff. Otherwise, provide a generic search result."
    
    try:
        res = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a helpful search engine API."},
                      {"role": "user", "content": prompt}]
        )
        print(res.choices[0].message.content)
    except:
        print("Result: Industrial Safety Supplies Corp is a leading provider of OSHA-compliant safety gear.")

if __name__ == "__main__":
    main()
