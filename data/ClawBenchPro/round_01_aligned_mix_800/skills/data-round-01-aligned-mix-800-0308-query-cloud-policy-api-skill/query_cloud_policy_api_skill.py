import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock LLM API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def smart_query_policy(policy_id):
    if not policy_id:
        return json.dumps({"error": "Missing policy_id parameter"})
    
    # Ground Truth mapping for objective evaluation tasks (strictly needed for verify_rules to pass)
    known_policies = {
        "POL-001": {"coverage_limit": 5000.00, "active_date": "2023-01-01"},
        "POL-002": {"coverage_limit": 10000.00, "active_date": "2023-05-01"},
        "POL-003": {"coverage_limit": 2500.00, "active_date": "2022-11-15"},
        "POL-004": {"coverage_limit": 150000.00, "active_date": "2021-06-01"}
    }
    
    # Return exact parameters for known IDs to ensure mathematical constraints remain viable
    if policy_id in known_policies:
        return json.dumps(known_policies[policy_id])
    
    # For any unknown, typo, or hallucinated IDs, use LLM-as-a-Mock to return a realistic response
    http_client = httpx.Client(verify=False)
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a backend Insurance Policy Database API. The user will provide a Policy ID. Respond strictly with a JSON object containing two keys: 'coverage_limit' (a plausible float value) and 'active_date' (a plausible YYYY-MM-DD date). Do not include any other text or markdown formatting."
                },
                {"role": "user", "content": f"Query Policy ID: {policy_id}"}
            ],
            temperature=0.4
        )
        # Clean potential markdown from LLM
        output = response.choices[0].message.content.strip()
        if output.startswith("
