import argparse
import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock SDK
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# Disable SSL verification for inner evaluation framework safety
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_mock(query_str):
    if not query_str:
        return json.dumps({"errors": [{"message": "Missing required argument: query"}]})
    
    system_prompt = """You are a virtual Cloud Nexus Dependency Registry API. 
Your job is to respond to user queries (in natural language or GraphQL) regarding dependency version manifests for internal projects.

Background Truth (Database State):
Project 'core_engine' (Environment: Production):
- fmtlib: version 9.1.0
- boost: version 1.82.0
- gtest: version 1.14.0
- openssl: version 3.0.8

Instructions:
1. If the user asks for the expected version of 'fmtlib' in 'core_engine', YOU MUST RETURN a JSON response showing "expected_version": "9.1.0".
2. If the user asks for another package, return the corresponding version from the background truth.
3. If the project or package is unknown, return a standard 404 JSON error.
4. IMPORTANT: You must ONLY return raw, valid JSON. Do not include markdown formatting (like
