import os
import sys
import json
import httpx
import argparse
from openai import OpenAI

# Required environment variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o-mini")

# Disable SSL verification to prevent evaluation sandbox network issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_db(name):
    if not name:
        return '{"error": "Missing volunteer name parameter."}'
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are the MedAuth National Volunteer Database API. The ONLY authorized volunteers globally are: Sarah Chen, Michael Ross, Elena Rodriguez, David Kim. If the user queries exactly one of these names, reply STRICTLY in JSON format: {\"status\": \"authorized\", \"name\": \"<name>\"}. If the name is anything else (e.g., John Doe, Unknown, empty, etc.), reply STRICTLY in JSON: {\"status\": \"unregistered\", \"name\": \"<name>\"}. Do not output markdown code blocks (like
