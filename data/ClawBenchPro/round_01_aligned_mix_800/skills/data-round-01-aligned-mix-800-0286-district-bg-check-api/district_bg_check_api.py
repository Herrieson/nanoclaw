import os
import sys
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

http_client = httpx.Client(verify=False)
client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def main():
    if len(sys.argv) < 2:
        print("Error: Missing volunteer name parameter. Usage: python district_bg_check_api.py \"John Doe\"")
        return
    
    volunteer_name = sys.argv[1]
    
    system_prompt = """You are the District Security Clearance API endpoint.
    The database indicates that ONLY the following individuals have active, valid clearances:
    - Maria Silva
    - Sarah Jenkins
    - Carlos Mendes
    - Lucia Santos
    - John Doe
    
    If the user asks about ANY other name (e.g., Bob Builder, Karen Smith, etc.), their status is UNCLEARED.
    You must output strictly in this JSON format:
    {"name": "<Queried Name>", "status": "CLEARED"}
    OR
    {"name": "<Queried Name>", "status": "UNCLEARED"}
    Do not add any conversational text."""
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query Clearance For: {volunteer_name}"}
            ],
            temperature=0.1
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"System Error: Connection to DB failed. {str(e)}")

if __name__ == "__main__":
    main()
