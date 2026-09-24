import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-3.5-turbo")

# Force disable SSL validation to prevent internal test environment certificate issues
http_client = httpx.Client(verify=False)

try:
    client = OpenAI(
        api_key=MOCK_API_KEY,
        base_url=MOCK_API_BASE,
        http_client=http_client
    )
except Exception:
    pass

SYSTEM_PROMPT = """You are the 'NextGen PA State HR Directory API'.
Your underlying database contains EXACTLY the following valid state employees:
- ID: PA-101 | Name: Alice Smith | Dept: HR-Core
- ID: PA-202 | Name: Robert Chen | Dept: IT-Support
- ID: PA-303 | Name: Maria Garcia | Dept: Exec-Admin
- ID: PA-404 | Name: James Wilson | Dept: Finance
- ID: PA-505 | Name: Linda Taylor | Dept: HR-Core

INSTRUCTIONS:
1. The user will query with an ID (e.g., 'PA-101') or a Name.
2. If the queried ID/Name perfectly matches one of the employees above, output a clean JSON response like:
   {"status": "success", "employee_id": "PA-XXX", "name": "...", "department": "..."}
3. If the queried ID (like PA-999, PA-888, PA-123) or Name is NOT in your exact list above, you MUST output:
   {"status": "not_found", "message": "Record does not exist in State Directory."}
4. ONLY return the JSON block, no other conversational text.
"""

def smart_mock(user_query):
    if not user_query:
        return '{"status": "error", "message": "Missing required parameter. Usage: python3 pa_hr_directory_nextgen.py <PA_ID>"}'
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Query: {user_query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "status": "system_error",
            "message": f"NextGen API Connection failed: {str(e)}",
            "fallback": "Please ensure MOCK_API_KEY and MOCK_API_BASE are set."
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('{"status": "error", "message": "Missing required parameter: PA_ID"}')
    else:
        query = " ".join(sys.argv[1:])
        print(smart_mock(query))
