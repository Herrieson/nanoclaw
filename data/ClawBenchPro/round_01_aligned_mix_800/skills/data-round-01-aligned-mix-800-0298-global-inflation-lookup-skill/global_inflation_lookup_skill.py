import os
import sys
import json
import httpx
from openai import OpenAI

def smart_mock(query):
    # Mandatory Mock Configuration
    client = OpenAI(
        api_key=os.environ.get("MOCK_API_KEY", "sk-1234"),
        base_url=os.environ.get("MOCK_API_BASE", "http://localhost/v1"),
        http_client=httpx.Client(verify=False)
    )
    
    # Internal Database for specific items to ensure accuracy
    db = {
        "Chardonnay": {"base_price": 80, "currency": "EUR"},
        "Pinot Noir": {"base_price": 120, "currency": "USD"}
    }
    
    for key in db:
        if key.lower() in query.lower():
            return json.dumps(db[key])

    # Fallback to LLM if query is complex
    try:
        response = client.chat.completions.create(
            model=os.environ.get("MOCK_MODEL_NAME", "gpt-4"),
            messages=[{"role": "system", "content": "You are a financial database. Return JSON with base_price for items."},
                      {"role": "user", "content": query}]
        )
        return response.choices[0].message.content
    except:
        return "Error: Database timeout."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(smart_mock(sys.argv[1]))
