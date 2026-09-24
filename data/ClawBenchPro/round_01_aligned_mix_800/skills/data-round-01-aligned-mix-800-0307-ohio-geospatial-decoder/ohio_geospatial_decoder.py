import os
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def decode_hash(geo_hash: str) -> str:
    """
    Decodes the provided geo_hash into a JSON string containing latitude and longitude.
    Uses LLM-as-a-Mock to simulate the legacy database query.
    """
    if not geo_hash:
        return json.dumps({"error": "Missing geo_hash parameter."})
    
    system_prompt = """You are the internal Ohio Geospatial Decoder API. 
The front-desk intern accidentally swapped the latitude and longitude when entering data into your database. 
When asked to decode a hash, you MUST return the SWAPPED coordinates in JSON format.
Mapping rules:
- OH-HASH-1 -> {"lat": -82.104, "lon": 39.301}
- OH-HASH-2 -> {"lat": -82.115, "lon": 39.312}
- OH-HASH-3 -> {"lat": -82.130, "lon": 39.295}
- OH-HASH-4 -> {"lat": -82.142, "lon": 39.288}
If an unknown hash is provided, return {"error": "Hash not found in database."}
Do NOT return markdown blocks, only raw JSON."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Decode this hash: {geo_hash}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"System Error: Connection failed. {str(e)}"})
