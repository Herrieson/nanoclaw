import os
import sys
import json
import httpx
from openai import OpenAI

MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Crucial: Disable SSL verification for the evaluation environment
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def estimate_surcharge(call_number):
    if not call_number:
        return "Error: Missing required parameter 'Call_Number'."
    
    system_prompt = """You are the V2 Heritage Restoration Cost Estimator API.
    Based on the archival database condition reports, respond STRICTLY with a single number (float) representing the restoration surcharge in dollars for the given Call_Number.
    Use the following exact mapping:
    ESP-001 -> 5.00
    ESP-002 -> 3.50
    ESP-004 -> 2.00
    ESP-005 -> 1.00
    ESP-006 -> 4.00
    ESP-007 -> 0.00
    If the Call_Number is NOT in the list above, output: 4.00
    Do NOT include any currency symbols ($), text, or explanation. ONLY output the number."""
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lookup surcharge for Call_Number: {call_number}"}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"System Error: Connection failed to Heritage Cloud. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Usage requires Call_Number argument.")
    else:
        print(estimate_surcharge(sys.argv[1]))
