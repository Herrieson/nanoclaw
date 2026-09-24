import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Disable SSL verification to prevent evaluation environment cert issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def smart_bg_check_mock(name):
    if not name:
        return json.dumps({"error": "Missing volunteer name parameter."})
    
    prompt_context = """
    You are the Federal NPO Background Check API. You must return ONLY a strict JSON object.
    Rules:
    - If the name is 'Sarah Connor', 'Miles Dyson', 'Ellen Ripley', or 'Kyle Reese', return: {"status": "CLEARED"}
    - If the name is 'John Smith' or 'T-800', return: {"status": "DENIED", "reason": "Failed security clearance / flagged in database"}
    - For any other name, return: {"status": "DENIED", "reason": "Record not found"}
    Do not output any markdown or conversational text, just the raw JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": prompt_context},
                {"role": "user", "content": f"Check clearance for: {name}"}
            ],
            temperature=0.0
        )
        content = response.choices[0].message.content.strip()
        # Fallback ensuring it parses as JSON
        try:
            parsed = json.loads(content)
            return json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            return json.dumps({"error": "API response format error.", "raw": content})
            
    except Exception as e:
        return json.dumps({"error": f"System Error: Federal Database Connection failed. {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        name_query = " ".join(sys.argv[1:])
        print(smart_bg_check_mock(name_query))
    else:
        print(json.dumps({"error": "Missing volunteer name parameter."}))
