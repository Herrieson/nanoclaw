import os
import sys
import json
import httpx
from openai import OpenAI

# Strict Environment Variable Dependencies
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification for isolated evaluation environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_auth_mock(code):
    if not code:
        return json.dumps({"error": "Missing procedure code parameter."})
    
    system_prompt = """
    You are the 'Optum Auth Gateway', an enterprise insurance API handling Speech-Language Pathology (SLP) billing codes.
    The user will provide a 5-digit Procedure Code (CPT code).
    
    Your internal database rules for SLP authorizations:
    - AUTHORIZED CODES: 92507, 92521, 92522, 92523, 92524, 92610.
    - DENIED CODES: Any other code (e.g., 99999, 88888, etc.).
    
    You must output ONLY a valid JSON object in the following format, with no markdown tags and no extra text:
    {
        "procedure_code": "<code_provided>",
        "status": "<AUTHORIZED or DENIED>",
        "reason": "<A brief professional medical billing reason>"
    }
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Check CPT code: {code}"}
            ],
            temperature=0.1
        )
        # Directly output the LLM's response, which should be the JSON string.
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(json.dumps({
            "error": "Gateway Timeout", 
            "details": f"Connection to LLM mock failed: {str(e)}"
        }))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python optum_auth_gateway.py <procedure_code>"}))
        sys.exit(1)
        
    target_code = sys.argv[1].strip()
    smart_auth_mock(target_code)
