import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables for Mock Verification
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification as strictly requested
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Ground truth hidden in the mock skill
TRUTH_DB = {
    "SKU-101": {"part_name": "chrome_wheels", "quantity": "20"},
    "SKU-102": {"part_name": "chassis_frame", "quantity": "0"},
    "SKU-103": {"part_name": "exhaust_pipe", "quantity": "-2"},
    "SKU-104": {"part_name": "steering_wheel", "quantity": "5"},
    "SKU-201": {"part_name": "cab_roof", "quantity": "1"},
    "SKU-202": {"part_name": "mud_flaps", "quantity": "0"},
    "SKU-203": {"part_name": "front_grille", "quantity": "none"},
    "SKU-204": {"part_name": "headlights", "quantity": "4"}
}

def smart_mock(user_params):
    if not user_params:
        return "Error: Missing required parameters. Please provide SKU numbers."
    
    system_prompt = f"""
    You are the 'Texas Hobby DB' virtual API. 
    The user will provide a string containing SKU numbers.
    You must parse their input, look up the SKUs in the following exact Ground Truth database, and return a clean JSON list of objects containing 'sku', 'part_name', and 'quantity'.
    
    Ground Truth Database:
    {json.dumps(TRUTH_DB, indent=2)}
    
    If an SKU is not found in the database, return its part_name as "Unknown" and quantity as null.
    ONLY return valid JSON format, no markdown blocks or conversational text.
    """

    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"User Query: {user_params}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"System Error: Connection failed. {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python texas_hobby_db_skill.py '<SKU_LIST>'")
    else:
        result = smart_mock(sys.argv[1])
        print(result)
