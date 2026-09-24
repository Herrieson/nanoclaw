import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)

def run(package_name, grade):
    prompt = f"""
    You are an insurance policy database. Return the tax percentage for:
    Package: {package_name}
    Grade: {grade}
    
    Rule: If Premium, return 0.10. If Standard, return 0.00. 
    Format: Only return the JSON object: {{"percentage": 0.xx}}
    """
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content
    except Exception:
        # Fallback if LLM fails
        if "Premium" in package_name:
            return json.dumps({"percentage": 0.1})
        return json.dumps({"percentage": 0.0})

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(run(sys.argv[1], sys.argv[2]))
