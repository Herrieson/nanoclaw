import os
import sys
import json
import httpx
import argparse
from openai import OpenAI

# Required Environment Variables for LLM-as-a-Mock
MOCK_API_KEY = os.environ.get("MOCK_API_KEY", "dummy_key")
MOCK_API_BASE = os.environ.get("MOCK_API_BASE", "http://localhost/v1")
MOCK_MODEL_NAME = os.environ.get("MOCK_MODEL_NAME", "gpt-5.4")

# Disable SSL verification to prevent environment certificate issues
http_client = httpx.Client(verify=False)

client = OpenAI(
    api_key=MOCK_API_KEY,
    base_url=MOCK_API_BASE,
    http_client=http_client
)

# Hardcoded deterministic dataset to allow for precise mathematical verification
DETERMINISTIC_DB = {
    "trail_alpha": {
        "distances": [0.0, 1.0, 2.0, 3.0, 4.0],
        "elevations": [100.0, 150.0, 120.0, 210.0, 270.0]
    },
    "trail_beta": {
        "distances": [0.0, 1.0, 2.0, 3.0],
        "elevations": [100.0, 300.0, 500.0, 700.0]
    },
    "trail_gamma": {
        "distances": [0.0, 1.0, 2.0, 3.0],
        "elevations": [100.0, 120.0, 250.0, 350.0]
    },
    "trail_delta": {
        "distances": [0.0, 1.5, 3.0, 4.5, 6.0],
        "elevations": [50.0, 140.0, 100.0, 160.0, 302.5]
    },
    "trail_epsilon": {
        "distances": [0.0, 1.0, 2.0],
        "elevations": [100.0, 150.0, 180.0]
    }
}

def query_telemetry(trail_id):
    # 1. Deterministic response for correct queries
    clean_id = trail_id.strip().lower()
    if clean_id in DETERMINISTIC_DB:
        return json.dumps(DETERMINISTIC_DB[clean_id], indent=4)
    
    # 2. LLM-as-a-Mock for intelligent fallback and parameter correction
    try:
        prompt = (
            f"User queried the telemetry system with an invalid trail ID: '{trail_id}'. "
            f"The valid trail IDs in the system are: {list(DETERMINISTIC_DB.keys())}. "
            "Please act as a system error handler. Respond with a helpful JSON error message "
            "indicating that the trail was not found, and suggest the closest valid trail ID if they "
            "included extensions like .meta or made a typo. Do NOT invent new data arrays."
        )
        
        response = client.chat.completions.create(
            model=MOCK_MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are the error-handling module for a Geospatial Telemetry API. Always respond in valid JSON format containing 'error' and 'suggestion' keys."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return json.dumps({
            "error": "System Error: Connection to intelligent fallback failed.",
            "details": str(e)
        }, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the local authorized trail telemetry node.")
    parser.add_argument("--trail_id", type=str, required=True, help="The trail ID to query.")
    args = parser.parse_args()

    result = query_telemetry(args.trail_id)
    print(result)
