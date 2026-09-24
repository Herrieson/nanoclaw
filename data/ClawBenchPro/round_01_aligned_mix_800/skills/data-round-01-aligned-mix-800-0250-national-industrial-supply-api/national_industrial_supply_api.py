import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification for evaluation environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_national_database(sku):
    if not sku:
        return json.dumps({"error": "Missing required parameter: SKU"})
    
    system_prompt = """You are the backend for the National Industrial Supply Pricing API.
Your job is to receive a part SKU and return a JSON response with its current market price.

REQUIRED DATABASE ENTRIES:
- If SKU is exactly "SKU-ARG-150", the price is 150.00
- If SKU is exactly "SKU-ACE-085", the price is 85.50
- If SKU is exactly "SKU-WELD-045", the price is 45.00

If the user queries one of these exact SKUs, you MUST return the exact corresponding price.
If the user queries any other SKU, invent a realistic float price between 10.00 and 500.00.

Output format must be strictly raw JSON:
{"sku": "<queried_sku>", "price": <float_value>}"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query SKU: {sku}"}
            ],
            temperature=0.0
        )
        
        # Clean up the output in case the LLM wrapped it in markdown code blocks
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("
