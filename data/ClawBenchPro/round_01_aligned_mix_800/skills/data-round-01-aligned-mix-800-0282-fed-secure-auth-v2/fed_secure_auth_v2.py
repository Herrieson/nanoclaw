import os
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification for robust local evaluation
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def fed_secure_auth_v2(badge_id: str) -> str:
    if not badge_id:
        return '{"error": "Missing required parameter: badge_id"}'
    
    # Context injected into the LLM mock to ensure deterministic facts for the evaluation
    system_prompt = """You are the backend of the FedSecure Auth API V2. 
    Your job is to verify if a given Badge ID is authorized.
    
    TRUTH DATA (Authorized IDs):
    - N-201
    - N-202
    - N-203
    - D-101
    - A-505
    
    Rules:
    1. If the user provides an ID from the Truth Data list, return a JSON with status "AUTHORIZED".
    2. If the user provides any other ID, return a JSON with status "UNAUTHORIZED".
    3. Output MUST be purely a JSON string like: {"badge_id": "...", "status": "..."} without markdown blocks.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Check this Badge ID: {badge_id}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({
            "error": "System Error",
            "message": f"V2 API connection failed due to mock server error: {str(e)}"
        })
