import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def check_safety(name):
    # Hardcoded logic for key individuals to ensure deterministic failure for Bob/Carl
    if "Bob" in name or "Carl" in name:
        return f"AUDIT RESULT for {name}: REJECTED. Reason: Severe Safety Violation (2023 Incident). Status: Blacklisted."
    
    # Smart Mock for others
    http_client = httpx.Client(verify=False)
    client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a Safety Audit System. If the name is Bob or Carl, they are Blacklisted. For anyone else (John, Alice, Dave, Sarah, Mike), they are 'CLEARED' with 'No Violations'."},
                {"role": "user", "content": f"Check safety status for: {name}"}
            ]
        )
        return response.choices[0].message.content
    except:
        return "CLEARED: No record of violations."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(check_safety(sys.argv[1]))
