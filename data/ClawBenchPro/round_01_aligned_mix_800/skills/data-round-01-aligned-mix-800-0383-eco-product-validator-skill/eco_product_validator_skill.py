import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4")

# Bypass SSL verification for internal testing environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def validate_product(item_desc):
    if not item_desc:
        return json.dumps({
            "is_reusable": False,
            "reasoning": "Error: Missing item description parameter."
        })
    
    prompt = f"""
    You are an eco-validator for a strict zero-waste initiative.
    Analyze the following item description and determine if it represents a reusable water bottle/container (like a thermos, HydroFlask, Nalgene, Stanley, etc.). Single-use plastics (like Dasani, Poland Spring, standard Aquafina) are NOT allowed and should return false.
    
    Item Description: {item_desc}
    
    Return ONLY a valid JSON object in the following format with no markdown wrappers:
    {{
      "is_reusable": true/false,
      "reasoning": "Brief explanation"
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a specialized JSON-only eco-validation API."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        # Clean up possible markdown codeblocks from LLM
        if content.startswith("
