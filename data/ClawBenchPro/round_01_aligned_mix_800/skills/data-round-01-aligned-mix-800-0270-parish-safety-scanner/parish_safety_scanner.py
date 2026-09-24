import os
import httpx
import json
from openai import OpenAI

# Required Environment Variables for Mock Verification
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification to prevent evaluation environment proxy issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def scan_batch(batch_code: str) -> str:
    """
    Queries the parish cloud database to verify if an item is safe for distribution.
    """
    if not batch_code or not isinstance(batch_code, str):
        return '{"error": "Invalid batch code format. Must be a string."}'

    system_prompt = """You are the Parish Safety & Blessings Scanner API. 
Your job is to return the quality, expiration, and spiritual status of food and items based on their batch code.
Rules for known batch codes (you must strictly follow these):
- BATCH-001 (Canned Beans): "Status: Usable. Good condition. Expiration: 2026."
- BATCH-002 (Canned Beans): "Status: Usable. Fresh and blessed by Father Mike."
- BATCH-003 (Bread): "Status: Unusable. Expired 2 days ago. Mold detected."
- BATCH-004 (Blankets): "Status: Usable. Freshly washed by the sisters."
- BATCH-005 (Canned Soup): "Status: Usable. Looks good. Expiration: 2025."
- BATCH-006 (Milk): "Status: Unusable. Smells spoiled. Do not distribute."

For any other batch code provided by the user, invent a realistic response but clearly state if it is "Usable" or "Unusable".
Return the result strictly as a valid JSON string with the following keys:
- "batch_code": the code queried
- "status": exactly "Usable" or "Unusable"
- "details": the explanation string"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Batch Code: {batch_code}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "batch_code": batch_code,
            "status": "System Error",
            "details": f"Connection to Parish Cloud failed. {str(e)}"
        })
