import os
import httpx
from openai import OpenAI

def service(query):
    MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
    MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
    MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))

    prompt = f"You are a local property registry database. Provide a brief, realistic background check for: {query}. If the name is 'Zodiac Killer', flag it as highly suspicious. If 'Unknown Stranger', say no record found."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"Registry Record for {query}: No prior evictions found. Identity verified."
