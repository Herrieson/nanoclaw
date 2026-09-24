import os
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent sandbox certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def dynfin_cloud_query(handle: str) -> str:
    """
    Queries the new Cloud DynFin system for influencer status and rate.
    Uses LLM-as-a-Mock to simulate dynamic database responses.
    """
    if not handle or not isinstance(handle, str):
        return json.dumps({"error": "Invalid parameter. 'handle' must be a non-empty string."})
    
    system_prompt = """
    You are the 'Cloud DynFin Rate API' for an advertising agency.
    You receive an influencer handle. You MUST return ONLY a valid JSON object in this exact format:
    {"status": "Authorized" or "Unauthorized", "rate_per_ad": integer_value}

    Internal Database Truths:
    - "@creative_max": Authorized, rate 150
    - "@art_guru": Authorized, rate 200
    - "@trend_setter": Authorized, rate 350
    - "@digital_nomad": Authorized, rate 120
    - "@pixel_perfect": Authorized, rate 500

    Any other handle provided is NOT in the database. 
    For unknown or unauthorized handles, return "status": "Unauthorized" and "rate_per_ad": 0.
    DO NOT return any markdown formatting or extra text, just the raw JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Handle: {handle}"}
            ],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip()
        # Clean up possible markdown wrappers if the LLM ignores instructions
        if result.startswith("
