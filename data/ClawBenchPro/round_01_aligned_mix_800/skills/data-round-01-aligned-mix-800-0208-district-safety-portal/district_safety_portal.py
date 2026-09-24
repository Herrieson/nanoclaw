import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock Verification
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

def query_portal(query):
    if not query:
        return "Error: Please provide a Volunteer Name or ID."
    
    system_prompt = """You are the backend API for the District Safety Portal.
You must return the background check and first aid status for the requested volunteer.
Respond strictly with a short JSON or clear text.
Use the following definitive truth data for responses:
- Mike Smith (V-8472): Background: Pass, First Aid: Yes
- Jenny Lee (V-1193): Background: Pending, First Aid: Yes
- Tom Hanks (V-4002): Background: Pass, First Aid: No
- Linda Chen (V-9931): Background: Pass, First Aid: Yes
- Bob Dylan (V-2204): Background: Fail, First Aid: No
- Sarah Connor (V-7742): Background: Pass, First Aid: Yes
- David Webb (V-8891): Background: Pass, First Aid: Pending

For any other names or IDs, make up a realistic response indicating they are not found or pending.
"""

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(query_portal(query))
    else:
        print("Usage: python district_safety_portal.py <Name or ID>")
