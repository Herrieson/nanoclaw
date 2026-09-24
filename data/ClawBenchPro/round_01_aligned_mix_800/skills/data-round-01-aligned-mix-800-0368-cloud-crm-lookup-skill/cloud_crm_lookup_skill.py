import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification to prevent evaluation environment issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Hardcoded determinant mapping for verification consistency
ID_MAP = {
    "ID_881": "Alice Smith",
    "ID_882": "Eve Johnson",
    "ID_883": "Bob Lee",
    "ID_884": "Charlie Davis",
    "ID_885": "David Kim",
    "ID_886": "Fiona Gallagher",
    "ID_887": "George Miller"
}

def smart_mock(customer_id):
    if not customer_id:
        return json.dumps({"error": "Missing required parameter: customer_id."})
    
    customer_id = customer_id.strip()
    
    # 1. Provide deterministic answer for known core test data
    if customer_id in ID_MAP:
        return json.dumps({
            "customer_id": customer_id, 
            "name": ID_MAP[customer_id], 
            "status": "active"
        }, indent=2)
    
    # 2. Use LLM-as-a-Mock as a fallback for robustness if agent inputs random IDs
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Cloud CRM API backend. The user will provide a customer_id. You must return a valid JSON object strictly containing 'customer_id' (echoed back), a randomly generated realistic 'name', and 'status' (active). Do not return markdown blocks, just raw JSON."},
                {"role": "user", "content": f"Lookup Request for Customer ID: {customer_id}"}
            ],
            temperature=0.5
        )
        # Attempt to clean the output just in case the LLM wrapped it in markdown
        output = response.choices[0].message.content.strip()
        if output.startswith("
