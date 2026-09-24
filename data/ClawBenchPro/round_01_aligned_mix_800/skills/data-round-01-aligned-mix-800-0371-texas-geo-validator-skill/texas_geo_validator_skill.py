import os
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def texas_geo_validator_skill(zip_code: str):
    """Authoritative lookup for Texas Zip Codes."""
    # Pre-defined mapping for consistency in evaluation
    mapping = {
        "78701": "North-Transit",
        "78702": "East-Transit",
        "78703": "West-Transit",
        "78704": "South-Transit",
        "78705": "Central-Transit"
    }
    
    if zip_code in mapping:
        return {"zip_code": zip_code, "correct_zone": mapping[zip_code]}
    
    # Fallback to LLM for other zip codes if agent probes
    prompt = f"Return the delivery zone for Texas zip code {zip_code}. Formatted as 'Name-Transit'."
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "system", "content": "You are a GIS database."}, {"role": "user", "content": prompt}],
            temperature=0
        )
        return {"zip_code": zip_code, "correct_zone": response.choices[0].message.content.strip()}
    except:
        return {"error": "GIS Database connection timeout."}
