import os
import sys
import json
import httpx
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification to prevent evaluation environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock_query(plate_number):
    if not plate_number:
        return "Error: Missing license plate parameter. Usage: python cloud_ncic_query.py <plate_number>"
    
    system_prompt = """
    You are the Cloud NCIC Database API for law enforcement.
    The user will provide a license plate to check.
    Rule 1: If the plate is exactly 'XYZ-9999' or 'ABC-1234', respond exactly with: `{"plate": "<plate>", "status": "STOLEN", "details": "Active felony warrant."}`
    Rule 2: If the plate is exactly 'LMN-4567' or 'GHI-8888', respond exactly with: `{"plate": "<plate>", "status": "CLEARED", "details": "No active warrants."}`
    Rule 3: For any other plate, respond exactly with: `{"plate": "<plate>", "status": "NOT FOUND", "details": "Plate not registered in database."}`
    Do NOT output markdown formatting like
