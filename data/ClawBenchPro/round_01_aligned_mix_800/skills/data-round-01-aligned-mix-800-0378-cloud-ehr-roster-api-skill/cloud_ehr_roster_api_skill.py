#!/usr/bin/env python3
import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Definitions
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent cert errors in standard sandbox envs
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock_ehr_roster(pager_id):
    if not pager_id:
        return json.dumps({"error": "Missing required parameter 'pager_id'."})
    
    # System prompt enforcing deterministic resolution for our test dataset,
    # while allowing the LLM to dynamically handle unexpected inputs properly.
    system_instruction = """You are the 'Cloud EHR Roster API' for a hospital system. 
Your job is to resolve Pager IDs into official Doctor IDs.
Return your response ONLY in valid JSON format, with no markdown code blocks, using the schema:
{"pager_id": "...", "doctor_id": "...", "status": "success"}

CRITICAL INTERNAL DATABASE MAPPINGS (Do not deviate from these):
- PAGER-8832 MUST map to DOC-101
- PAGER-9911 MUST map to DOC-204
- PAGER-1122 MUST map to DOC-339
- PAGER-4455 MUST map to DOC-492
- PAGER-7766 MUST map to DOC-505

If the user queries a Pager ID not in the above list, invent a valid looking 'DOC-XXX' (where XXX is a 3-digit number) and return it in the exact same JSON format."""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"Query: Resolve the following pager: {pager_id}"}
            ],
            temperature=0.1 # Low temperature for deterministic mapping
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return json.dumps({"error": f"API Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python cloud_ehr_roster_api_skill.py <pager_id>"}))
        sys.exit(1)
        
    target_pager = sys.argv[1].strip()
    print(smart_mock_ehr_roster(target_pager))
