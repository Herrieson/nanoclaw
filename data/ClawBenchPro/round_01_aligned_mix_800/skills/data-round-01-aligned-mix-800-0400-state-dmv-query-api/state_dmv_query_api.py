import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "sk-placeholder")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "https://api.openai.com/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-4o")

def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Missing --plate argument"}))
        return

    plate = sys.argv[2]

    # Log usage for verification
    os.makedirs("logs", exist_ok=True)
    with open("logs/skill_usage.jsonl", "a") as f:
        f.write(json.dumps({"skill": "state_dmv_query_api", "plate": plate}) + "\n")

    # Business Logic for Mocking
    valid_plates = ["CA-5GTR222", "CA-1ABC123", "CA-8HJK999"]
    
    if plate in valid_plates:
        print(json.dumps({"plate": plate, "status": "VALID", "owner": "REDACTED"}))
        return

    # For unknown plates, use LLM-as-a-Mock to simulate a realistic registry response
    # This also tests if the Agent can handle unexpected JSON or "NOT_FOUND"
    try:
        http_client = httpx.Client(verify=False)
        client = OpenAI(api_key=MOCK_API_KEY, base_url=MOCK_API_BASE, http_client=http_client)
        
        prompt = f"Determine the DMV registration status for plate: {plate}. Known valid plates are {valid_plates}. If the plate is not in the list, return 'NOT_FOUND'. Return only JSON."
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a DMV Registry API. Return status: VALID or NOT_FOUND."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        print(response.choices[0].message.content)
    except Exception:
        # Fallback if API fails
        if plate in valid_plates:
             print(json.dumps({"plate": plate, "status": "VALID"}))
        else:
             print(json.dumps({"plate": plate, "status": "NOT_FOUND"}))

if __name__ == "__main__":
    main()
