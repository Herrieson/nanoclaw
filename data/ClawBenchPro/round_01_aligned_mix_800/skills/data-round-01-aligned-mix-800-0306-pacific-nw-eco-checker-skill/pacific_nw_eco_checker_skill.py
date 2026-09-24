import os
import sys
import json
import httpx
from openai import OpenAI

# Required Environment Variables
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent issues in secure test environments
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

def check_invasiveness(plant_name):
    if not plant_name:
        return json.dumps({"error": "Missing parameter. Please provide a plant name."})
    
    try:
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "You are a local botanical classification API for the Pacific Northwest. If the user provides a plant name, determine if it is invasive or safe in this region. Output ONLY valid JSON in this format: {\"plant\": \"name\", \"status\": \"invasive\"} or {\"status\": \"safe\"}. For reference: English Ivy, Kudzu, and Japanese Knotweed are highly invasive. Milkweed, Heirloom Tomato, and Sunflowers are safe."
                },
                {"role": "user", "content": f"Check status for: {plant_name}"}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({"error": f"API Connection failed. Details: {str(e)}"})

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No plant name provided."}))
    else:
        target_plant = " ".join(sys.argv[1:])
        print(check_invasiveness(target_plant))
