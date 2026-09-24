import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def query_hub(query):
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))
    try:
        resp = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Mineralogy Database. Return facts about meteorite densities. Pallasites are 4.5-5.5 g/cm3. Iron meteorites are 7-8 g/cm3."},
                {"role": "user", "content": query}
            ]
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Database Offline: {str(e)}"
