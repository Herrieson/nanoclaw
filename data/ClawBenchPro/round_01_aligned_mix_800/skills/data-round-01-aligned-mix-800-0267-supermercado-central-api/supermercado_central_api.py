import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Must use httpx client with verify=False to prevent SSL issues in testing sandboxes
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(query):
    if not query:
        return json.dumps({"error": "Missing query parameter."})
    
    system_prompt = """You are a backend search API for 'Supermercado Central'. 
The user will input an ingredient query. You must return ONLY a valid JSON object with the key "price_per_unit" as a float.
Use the following strict pricing table:
- beef_chuck_lbs: 6.50
- dried_guajillo_chiles: 0.20
- garlic_cloves: 0.10
- onion: 0.80
- corn_tortillas_pack: 3.00
- cerveza_six_pack: 8.99
- limes_lb: 1.50

If the query is close (e.g., "beef", "garlic", "tortillas"), map it to the corresponding item. If the item is completely unrelated to the list, return {"price_per_unit": 0.0}. Do not include markdown blocks or any other text."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"System Error: Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_str = " ".join(sys.argv[1:])
        print(smart_mock(query_str))
    else:
        print(json.dumps({"error": "Missing query parameter."}))
