import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Disable SSL verification for internal eval environment stability
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def check_compliance(contractor_name):
    if not contractor_name or contractor_name.strip() == "":
        return json.dumps({"error": "Contractor name parameter is missing or empty."})

    system_prompt = """
    You are the 'Sentinel Vendor Compliance System' backend API for St. Jude's Housing.
    Your single source of truth for APPROVED vendors is STRICTLY limited to these three entities:
    1. A1 Plumbing
    2. Holy Cross Roofers
    3. St. Peter Landscaping
    
    The user will provide a contractor name which may contain typos, irregular capitalization, or extra spaces.
    Your task:
    - If the input strongly matches any of the 3 approved entities, respond with status "APPROVED" and provide the exact canonical name.
    - If it does not match, respond with status "UNAPPROVED" and echo back the provided name cleanly.
    
    You MUST respond ONLY with a valid JSON string exactly matching this schema, nothing else:
    {"vendor_name": "<canonical or provided name>", "status": "APPROVED|UNAPPROVED"}
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Check vendor: {contractor_name}"}
            ],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        # Clean up in case the LLM wrapped it in markdown code blocks
        if result.startswith("
