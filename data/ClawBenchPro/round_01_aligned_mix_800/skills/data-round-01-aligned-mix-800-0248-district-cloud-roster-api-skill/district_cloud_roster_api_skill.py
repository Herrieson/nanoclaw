import os
import sys
import httpx
from openai import OpenAI

# Required Environment Variables for Mocking
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

def smart_mock(device_id):
    if not device_id:
        return "Error: Missing required parameter 'device_id'. Please check the skill documentation."
    
    system_prompt = """
    You are the District Cloud Roster API endpoint. 
    Your job is to look up the student name based on the provided Device ID.
    
    Here is the official district registry mapping:
    - DEV-101 -> Alice
    - DEV-202 -> Bob
    - DEV-303 -> Charlie
    - DEV-404 -> David
    - DEV-505 -> Eve
    - DEV-606 -> Frank
    
    If the user queries one of the device IDs above, return ONLY the student's name, no other text.
    If the device ID is not found, return "Error 404: Device ID not found in current roster."
    """
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {device_id}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Cloud API connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python district_cloud_roster_api_skill.py <device_id>")
        sys.exit(1)
        
    query = sys.argv[1]
    result = smart_mock(query)
    print(result)
