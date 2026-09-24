import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent issues in sandboxed evaluation environments
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass # Will handle failure gracefully in the query execution

def query_erp(contractor_name):
    if not contractor_name or contractor_name.strip() == "":
        return '{"error": "Missing required parameter: contractor_name. Please check the skill documentation."}'

    system_prompt = """
    You are the backend API for the Oakbridge Construction Cloud ERP System.
    The user will provide a subcontractor name. You must respond ONLY with a raw JSON object. 
    Do not use markdown formatting (no
