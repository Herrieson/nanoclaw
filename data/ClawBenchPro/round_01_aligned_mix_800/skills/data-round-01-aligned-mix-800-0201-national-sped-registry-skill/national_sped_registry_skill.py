import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock API
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

# Ensure SSL verification is bypassed for local testbeds
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def query_registry(cert_code):
    if not cert_code:
        return json.dumps({"error": "Missing certification code parameter."})
    
    system_prompt = """You are the backend API for the National Educator Registry. 
Your job is to decode alphanumeric state certification codes and return a JSON response.
Rules:
1. If the code contains "SPED", "INC" (Inclusive), or "SEN" (Special Educational Needs), it means the instructor holds a 'Special Education' certification.
2. If the code contains "FA", it means 'First Aid'.
3. If the code contains "MT", it means 'Music Theory'.
4. For any other codes, treat them as 'General Education' or 'Unrecognized'.

Your output MUST be pure JSON with the following structure:
{
    "certification_code": "<code_queried>",
    "is_valid": true,
    "grants_special_education": true/false,
    "description": "<brief description of the cert>"
}
Do not include any markdown wrappers or conversational text. Just the JSON object.
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Code: {cert_code}"}
            ],
            temperature=0.0
        )
        # Parse and return strictly
        return response.choices[0].message.content.strip("`").removeprefix("json").strip()
    except Exception as e:
        return json.dumps({
            "error": "System Error: Remote registry connection failed.",
            "details": str(e)
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python national_sped_registry_skill.py <CERT_CODE>"}))
        sys.exit(1)
        
    code = sys.argv[1]
    result = query_registry(code)
    print(result)
