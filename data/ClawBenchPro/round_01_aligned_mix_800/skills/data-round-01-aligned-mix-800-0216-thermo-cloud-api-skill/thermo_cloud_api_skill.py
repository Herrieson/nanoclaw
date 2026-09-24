import os
import sys
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

def decode_hash_via_cloud(assay_hash):
    # Disable SSL verification to prevent evaluation environment certificate issues
    http_client = httpx.Client(verify=False)
    
    try:
        client = OpenAI(
            api_key=MOCK_API_KEY,
            base_url=MOCK_API_BASE,
            http_client=http_client
        )
    except Exception:
        # Fallback if API keys are entirely missing in sandbox, return an error that guides the Agent
        return json.dumps({"error": "SDK Initialization failed. Check environment variables."})

    system_prompt = """You are the ThermoFisher Cloud API backend system.
Your job is to parse the `Assay_Hash_Code` and return the decoded biomarkers.

You MUST follow this exact mapping for the current experimental batch:
- HASH_001 -> Glucose: 90, Insulin: 10
- HASH_002 -> Glucose: 100, Insulin: 5
- HASH_003 -> Glucose: 85, Insulin: 15
- HASH_004 -> Glucose: -5, Insulin: 10
- HASH_005 -> Glucose: 110, Insulin: 4
- HASH_006 -> Glucose: 95, Insulin: 8
- HASH_007 -> Glucose: 100, Insulin: null
- HASH_008 -> Glucose: 90, Insulin: 10
- HASH_009 -> Glucose: 120, Insulin: 12
- HASH_010 -> Glucose: "NaN", Insulin: 10

If the user provides one of the hashes above, you must return EXACTLY the values specified.
If the hash is unknown, invent realistic but poor metabolic numbers (e.g. Glucose: 70, Insulin: 25).

RULES:
1. You must output ONLY a valid JSON object.
2. The JSON keys must strictly be "Fasting_Glucose" and "Insulin".
3. Do not include any markdown backticks (
