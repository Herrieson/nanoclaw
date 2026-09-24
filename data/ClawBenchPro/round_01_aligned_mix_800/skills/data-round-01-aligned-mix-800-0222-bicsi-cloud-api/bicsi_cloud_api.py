import os
import sys
import json
import httpx
from openai import OpenAI
import argparse

# Must comply with API standards
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

SYSTEM_PROMPT = """You are the BICSI Telecom Certification Cloud API system.
Your goal is to parse the user's name query and return their active telecom certifications strictly in JSON format.

Ground Truth Database (Exact mappings):
- John Doe: ["FiberOptic", "Basic"]
- Maria Garcia: ["FiberOptic", "Cat6"]
- David Kim: ["FiberOptic", "Safety"]
- Sarah Lee: ["Cat6"]
- Tom Smith: ["Cat6"]
- Alex P: ["Basic"]
- Zack W: ["Basic"]
- Linda B: ["Safety"]

Rules:
1. If the queried name closely matches a name in the Ground Truth database, return their corresponding certifications.
2. If the queried name is not in the database at all, return an empty array [].
3. You must ONLY output a valid JSON object in the following format, with no markdown, no conversational text:
{"certifications": ["cert1", "cert2"]}
"""

def smart_mock(query_name):
    if not query_name:
        return "Error: Missing required parameter 'query_name'. Please provide a name to search."
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Lookup Name: {query_name}"}
            ],
            temperature=0.0 # Strict and deterministic for database lookups
        )
        result = response.choices[0].message.content.strip()
        
        # Strip markdown if LLM misbehaves
        if result.startswith("
