import os
import sys
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification for isolated evaluation environments
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    client = None

def query_db(code):
    if not code or not code.startswith("HVC-"):
        return json.dumps({"error": "Invalid format. Catalog codes must start with 'HVC-'."})
    
    if not client:
        # Fallback if OpenAI client fails to initialize in restricted envs
        fallback_db = {
            "HVC-1950-CC": {"item": "1950s workwear chore coat", "price": 55.00},
            "HVC-SILK-TIE": {"item": "vintage silk tie", "price": 18.50},
            "HVC-70S-PANTS": {"item": "1970s flared corduroy pants", "price": 22.75},
            "HVC-FEDORA": {"item": "vintage fedora hat", "price": 40.00}
        }
        return json.dumps(fallback_db.get(code, {"error": "Item not found in fallback catalog."}))
        
    system_prompt = """You are a virtual Vintage Clothing Database API.
    When the user queries a catalog code, you must return the exact item description and price in JSON format.
    
    Strict Knowledge Base:
    - Code: HVC-1950-CC -> {"item": "1950s workwear chore coat", "price": 55.00}
    - Code: HVC-SILK-TIE -> {"item": "vintage silk tie", "price": 18.50}
    - Code: HVC-70S-PANTS -> {"item": "1970s flared corduroy pants", "price": 22.75}
    - Code: HVC-FEDORA -> {"item": "vintage fedora hat", "price": 40.00}
    
    If the code matches one of the above, return ONLY the JSON dictionary. 
    If it does not match, return: {"error": "Item not found in catalog"}
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {code}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"Database System Error: Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        code_input = sys.argv[1].strip()
        print(query_db(code_input))
    else:
        print(json.dumps({"error": "Usage: python vintage_db_query.py <catalog_code>"}))
