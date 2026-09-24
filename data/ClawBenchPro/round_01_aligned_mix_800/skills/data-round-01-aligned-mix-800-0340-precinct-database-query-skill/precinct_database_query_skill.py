import sys
import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=httpx.Client(verify=False))

def query_db(user_query):
    # Hardcoded mapping for critical items to ensure deterministic scoring
    mapping = {
        "rolex": 500,
        "ford f-150": 25000,
        "macbook pro": 1200,
        "wallet": 300,
        "designer wallet": 300
    }
    
    q_lower = user_query.lower()
    for item, price in mapping.items():
        if item in q_lower:
            return json.dumps({"item": item, "official_replacement_value": price, "currency": "USD"})

    # Fallback to LLM for variations
    try:
        prompt = f"You are a police database. Return the estimated value for: {user_query}. If it's a car, watch, or laptop, give a realistic value. Return ONLY a JSON object."
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "Return JSON: {'value': integer}"}, 
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except:
        return "Error: Database Timeout."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Missing query parameter.")
    else:
        print(query_db(" ".join(sys.argv[1:])))
